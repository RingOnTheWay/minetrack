import os
import zipfile
import tarfile
import tempfile
import shutil

ARCHIVE_EXTENSIONS = {
    '.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2',
    '.tar.xz', '.txz', '.7z', '.rar',
}


def get_archive_extension(filename: str) -> str:
    lower = filename.lower()
    for ext in sorted(ARCHIVE_EXTENSIONS, key=len, reverse=True):
        if lower.endswith(ext):
            return ext
    return ''


def is_archive_file(filepath: str) -> bool:
    return bool(get_archive_extension(os.path.basename(filepath)))


def extract_archive(filepath: str, extract_dir: str) -> str:
    ext = get_archive_extension(os.path.basename(filepath))

    if ext == '.zip':
        with zipfile.ZipFile(filepath, 'r') as zf:
            zf.extractall(extract_dir)
    elif ext in ('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz'):
        with tarfile.open(filepath, 'r:*') as tf:
            tf.extractall(extract_dir)
    elif ext == '.7z':
        try:
            import py7zr
        except ImportError:
            raise ValueError('需要安装 py7zr 库来解压 7z 文件：pip install py7zr')
        with py7zr.SevenZipFile(filepath, 'r') as sz:
            sz.extractall(extract_dir)
    elif ext == '.rar':
        try:
            import rarfile
        except ImportError:
            raise ValueError('需要安装 rarfile 库来解压 RAR 文件：pip install rarfile')
        try:
            rf = rarfile.RarFile(filepath)
            rf.extractall(extract_dir)
            rf.close()
        except rarfile.NeedFirstVolume:
            raise ValueError('请提供 RAR 分卷的第一个文件')
        except rarfile.RarCannotExecute:
            raise ValueError('解压 RAR 文件需要安装 UnRAR 命令行工具')
    else:
        raise ValueError(f'不支持的压缩格式: {ext}')

    return _find_server_folder(extract_dir)


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


class ArchiveTempExtractor:
    def __init__(self):
        self._temp_dirs = []

    def extract(self, archive_path: str) -> str:
        temp_dir = tempfile.mkdtemp(prefix='minetrack_')
        self._temp_dirs.append(temp_dir)
        server_folder = extract_archive(archive_path, temp_dir)
        return server_folder

    def cleanup(self):
        for d in self._temp_dirs:
            try:
                shutil.rmtree(d, ignore_errors=True)
            except Exception:
                pass
        self._temp_dirs.clear()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()
