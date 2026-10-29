"""Verify that a packaged app contains only ARM64 Mach-O binaries."""
import pathlib
import subprocess
import sys


def main():
    bundle = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'dist/openMotor.app').resolve()
    executable = bundle / 'Contents/MacOS/openMotor'
    if not executable.is_file():
        sys.exit(f'Missing app executable: {executable}')
    headers = {
        bytes.fromhex(value) for value in (
            'feedface', 'cefaedfe', 'feedfacf', 'cffaedfe',
            'cafebabe', 'bebafeca', 'cafebabf', 'bfbafeca',
        )
    }
    checked = 0
    for path in bundle.rglob('*'):
        if path.is_symlink() or not path.is_file():
            continue
        with path.open('rb') as source:
            header = source.read(4)
        if header not in headers:
            continue
        architectures = subprocess.check_output(['/usr/bin/lipo', '-archs', str(path)], text=True).split()
        if architectures != ['arm64']:
            sys.exit(f'Unexpected architecture {architectures}: {path}')
        checked += 1
    if not checked:
        sys.exit('No Mach-O binaries found')
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(bundle)], check=True)
    print(f'Verified {checked} ARM64 binaries and app code signature: {bundle}')


if __name__ == '__main__':
    main()
