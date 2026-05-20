import os
import zipfile
import tarfile
import tempfile
import shutil
import logging

logger = logging.getLogger(__name__)

ARCHIVE_EXTENSIONS = {
    '.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2',
    '.tar.xz', '.txz', '.7z', '.rar',
}

MAP_FOLDER_NAMES = [
    ('world', ['world', 'world/dimensions/minecraft/overworld']),
    ('world_nether', ['world_nether', 'world/dimensions/minecraft/the_nether']),
    ('world_the_end', ['world_the_end', 'world/dimensions/minecraft/the_end']),
]


def get_archive_extension(filename: str) -> str:
    lower = filename.lower()
    for ext in sorted(ARCHIVE_EXTENSIONS, key=len, reverse=True):
        if lower.endswith(ext):
            return ext
    return ''


def is_archive_file(filepath: str) -> bool:
    return bool(get_archive_extension(os.path.basename(filepath)))


def _normalize_path(path: str) -> str:
    p = path.replace('\\', '/')
    while p.startswith('./'):
        p = p[2:]
    return p


def _is_stats_path(normalized: str) -> bool:
    if not normalized.endswith('.json'):
        return False
    parts = normalized.split('/')
    if 'stats' not in parts:
        return False
    stats_idx = parts.index('stats')
    if stats_idx == 0:
        return False
    parent = parts[stats_idx - 1]
    return parent in ('players', 'world')


def _is_needed_file(relative_path: str) -> bool:
    normalized = _normalize_path(relative_path)
    parts = normalized.split('/')
    basename = parts[-1]
    if basename in ('server.properties', 'usercache.json'):
        return True
    if _is_stats_path(normalized):
        return True
    return False


def _find_server_folder(extract_dir: str) -> str:
    world_path = os.path.join(extract_dir, 'world')
    if os.path.exists(world_path):
        return extract_dir
    for name in os.listdir(extract_dir):
        candidate = os.path.join(extract_dir, name)
        if os.path.isdir(candidate):
            if os.path.exists(os.path.join(candidate, 'world')):
                return candidate
    return extract_dir


class ArchiveReader:
    def __init__(self, archive_path: str):
        self.archive_path = archive_path
        self.ext = get_archive_extension(os.path.basename(archive_path))
        self._prefix = ''
        self._file_list = None
        self.needed_data = None

    def list_files(self):
        if self._file_list is not None:
            return self._file_list

        files = []
        if self.ext == '.zip':
            with zipfile.ZipFile(self.archive_path, 'r') as zf:
                for info in zf.infolist():
                    if not info.is_dir():
                        files.append((info.filename, info.file_size))
        elif self.ext in ('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz'):
            with tarfile.open(self.archive_path, 'r:*') as tf:
                for member in tf.getmembers():
                    if member.isfile():
                        files.append((member.name, member.size))
        elif self.ext == '.7z':
            import py7zr
            with py7zr.SevenZipFile(self.archive_path, 'r') as sz:
                for fi in sz.list():
                    if not fi.is_directory:
                        size = fi.uncompressed if hasattr(fi, 'uncompressed') else 0
                        files.append((fi.filename, size))
        elif self.ext == '.rar':
            import rarfile
            with rarfile.RarFile(self.archive_path) as rf:
                for info in rf.infolist():
                    if not info.is_dir():
                        files.append((info.filename, info.file_size))

        self._file_list = files
        self._detect_prefix()
        return files

    def _detect_prefix(self):
        for path, _ in self._file_list:
            normalized = _normalize_path(path)
            parts = normalized.split('/')
            if 'world' in parts:
                world_idx = parts.index('world')
                if world_idx == 0:
                    self._prefix = ''
                else:
                    orig_parts = path.replace('\\', '/').split('/')
                    self._prefix = '/'.join(orig_parts[:world_idx]) + '/'
                return
        self._prefix = ''

    def _strip_prefix(self, path):
        normalized = _normalize_path(path)
        if self._prefix:
            prefix_normalized = _normalize_path(self._prefix)
            if normalized.startswith(prefix_normalized):
                return normalized[len(prefix_normalized):]
        return normalized

    def get_needed_files(self):
        self.list_files()
        needed = []
        for path, size in self._file_list:
            relative = self._strip_prefix(path)
            if _is_needed_file(relative):
                needed.append(path)
        return needed

    def read_needed_gen(self):
        self.list_files()
        needed = self.get_needed_files()
        total = len(needed)

        self.needed_data = {
            'server_properties': None,
            'usercache': None,
            'stats': {},
        }

        logger.info(f"ArchiveReader: {self.archive_path}, ext={self.ext}, total_files={len(self._file_list)}, needed={total}, prefix='{self._prefix}'")
        if total > 0:
            logger.info(f"ArchiveReader: needed files sample: {needed[:5]}")

        if total == 0:
            logger.warning(f"ArchiveReader: no needed files found in {self.archive_path}")
            all_sample = [p for p, _ in self._file_list[:20]]
            logger.warning(f"ArchiveReader: file list sample: {all_sample}")
            return

        if self.ext == '.zip':
            with zipfile.ZipFile(self.archive_path, 'r') as zf:
                for i, member_path in enumerate(needed):
                    relative = self._strip_prefix(member_path)
                    normalized = _normalize_path(relative)
                    basename = normalized.split('/')[-1]

                    try:
                        content = zf.read(member_path).decode('utf-8', errors='ignore')
                    except Exception:
                        yield (i + 1, total, basename)
                        continue

                    if basename == 'server.properties':
                        self.needed_data['server_properties'] = content
                    elif basename == 'usercache.json':
                        self.needed_data['usercache'] = content
                    elif _is_stats_path(normalized):
                        uuid = basename[:-5]
                        self.needed_data['stats'][uuid] = content

                    yield (i + 1, total, basename)

        elif self.ext in ('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz'):
            needed_set = set(needed)
            extracted = 0
            with tarfile.open(self.archive_path, 'r:*') as tf:
                for member in tf:
                    if not member.isfile():
                        continue
                    if member.name not in needed_set:
                        continue

                    relative = self._strip_prefix(member.name)
                    normalized = _normalize_path(relative)
                    basename = normalized.split('/')[-1]
                    extracted += 1

                    try:
                        f = tf.extractfile(member)
                        content = f.read().decode('utf-8', errors='ignore') if f else ''
                    except Exception:
                        yield (extracted, total, basename)
                        continue

                    if basename == 'server.properties':
                        self.needed_data['server_properties'] = content
                    elif basename == 'usercache.json':
                        self.needed_data['usercache'] = content
                    elif _is_stats_path(normalized):
                        uuid = basename[:-5]
                        self.needed_data['stats'][uuid] = content

                    yield (extracted, total, basename)

        elif self.ext == '.7z':
            import py7zr
            temp_dir = tempfile.mkdtemp(prefix='minetrack_7z_')
            try:
                with py7zr.SevenZipFile(self.archive_path, 'r') as sz:
                    sz.extract(temp_dir, targets=needed)

                for i, member_path in enumerate(needed):
                    relative = self._strip_prefix(member_path)
                    normalized = _normalize_path(relative)
                    basename = normalized.split('/')[-1]

                    try:
                        file_path = os.path.join(temp_dir, member_path.replace('/', os.sep))
                        if not os.path.exists(file_path):
                            for root, dirs, files in os.walk(temp_dir):
                                for f in files:
                                    candidate = os.path.join(root, f)
                                    rel = os.path.relpath(candidate, temp_dir).replace(os.sep, '/')
                                    if _normalize_path(rel) == normalized:
                                        file_path = candidate
                                        break
                                else:
                                    continue
                                break
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        else:
                            content = ''
                    except Exception as e:
                        logger.warning(f"ArchiveReader 7z: error reading {member_path}: {e}")
                        yield (i + 1, total, basename)
                        continue

                    if not content:
                        logger.warning(f"ArchiveReader 7z: empty content for {member_path}")

                    if basename == 'server.properties':
                        self.needed_data['server_properties'] = content
                    elif basename == 'usercache.json':
                        self.needed_data['usercache'] = content
                    elif _is_stats_path(normalized):
                        uuid = basename[:-5]
                        self.needed_data['stats'][uuid] = content

                    yield (i + 1, total, basename)
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        elif self.ext == '.rar':
            import rarfile
            with rarfile.RarFile(self.archive_path) as rf:
                for i, member_path in enumerate(needed):
                    relative = self._strip_prefix(member_path)
                    normalized = _normalize_path(relative)
                    basename = normalized.split('/')[-1]

                    try:
                        content = rf.read(member_path).decode('utf-8', errors='ignore')
                    except Exception:
                        yield (i + 1, total, basename)
                        continue

                    if basename == 'server.properties':
                        self.needed_data['server_properties'] = content
                    elif basename == 'usercache.json':
                        self.needed_data['usercache'] = content
                    elif _is_stats_path(normalized):
                        uuid = basename[:-5]
                        self.needed_data['stats'][uuid] = content

                    yield (i + 1, total, basename)

    def selective_extract_gen(self, extract_dir):
        self.list_files()
        needed = self.get_needed_files()
        total = len(needed)

        if total == 0:
            return

        if self.ext == '.zip':
            with zipfile.ZipFile(self.archive_path, 'r') as zf:
                for i, member_path in enumerate(needed):
                    target_path = os.path.join(extract_dir, member_path.replace('/', os.sep))
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zf.open(member_path) as src, open(target_path, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    yield (i + 1, total)
        elif self.ext in ('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz'):
            needed_set = set(needed)
            extracted = 0
            with tarfile.open(self.archive_path, 'r:*') as tf:
                for member in tf:
                    if member.isfile() and member.name in needed_set:
                        tf.extract(member, extract_dir)
                        extracted += 1
                        yield (extracted, total)
        elif self.ext == '.7z':
            import py7zr
            with py7zr.SevenZipFile(self.archive_path, 'r') as sz:
                sz.extract(extract_dir, targets=needed)
                yield (total, total)
        elif self.ext == '.rar':
            import rarfile
            with rarfile.RarFile(self.archive_path) as rf:
                for i, member_path in enumerate(needed):
                    rf.extract(member_path, extract_dir)
                    yield (i + 1, total)

    def compute_map_sizes(self):
        self.list_files()
        result = []
        for map_name, possible_paths in MAP_FOLDER_NAMES:
            total_bytes = 0
            found = False
            for prefix_path in possible_paths:
                for path, file_size in self._file_list:
                    relative = self._strip_prefix(path)
                    normalized = _normalize_path(relative)
                    if normalized.startswith(prefix_path + '/'):
                        total_bytes += file_size
                        found = True
            if found:
                size_mb = round(total_bytes / (1024 * 1024), 2)
                result.append({'name': map_name, 'size': size_mb})
        return result

    def read_file_text(self, relative_path):
        self.list_files()
        actual_path = None
        for path, _ in self._file_list:
            if _normalize_path(self._strip_prefix(path)) == _normalize_path(relative_path):
                actual_path = path
                break

        if actual_path is None:
            return None

        try:
            if self.ext == '.zip':
                with zipfile.ZipFile(self.archive_path, 'r') as zf:
                    return zf.read(actual_path).decode('utf-8', errors='ignore')
            elif self.ext in ('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz'):
                with tarfile.open(self.archive_path, 'r:*') as tf:
                    member = tf.getmember(actual_path)
                    f = tf.extractfile(member)
                    if f:
                        return f.read().decode('utf-8', errors='ignore')
            elif self.ext == '.7z':
                import py7zr
                temp_dir = tempfile.mkdtemp(prefix='minetrack_7z_')
                try:
                    with py7zr.SevenZipFile(self.archive_path, 'r') as sz:
                        sz.extract(temp_dir, targets=[actual_path])
                    file_path = os.path.join(temp_dir, actual_path.replace('/', os.sep))
                    if not os.path.exists(file_path):
                        for root, dirs, files in os.walk(temp_dir):
                            for f in files:
                                candidate = os.path.join(root, f)
                                rel = os.path.relpath(candidate, temp_dir).replace(os.sep, '/')
                                if _normalize_path(rel) == _normalize_path(actual_path):
                                    file_path = candidate
                                    break
                            else:
                                continue
                            break
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            return f.read()
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
            elif self.ext == '.rar':
                import rarfile
                with rarfile.RarFile(self.archive_path) as rf:
                    return rf.read(actual_path).decode('utf-8', errors='ignore')
        except Exception:
            pass

        return None
