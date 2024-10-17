PythonでAxisを使うコード

## 使い方

```bash
git clone https://github.com/akubota-lab/cv-axis-python axis
cd axis
poetry install
poetry run python ptz.py
poetry run python ptz.py --ip 192.168.0.90 --username root --password password --resolution "1920x1080"
```

もしくは
```bash
poetry add git+https://github.com/akubota-lab/cv-axis-python
```