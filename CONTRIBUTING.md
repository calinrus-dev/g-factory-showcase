# Verificar la muestra

Python 3.12 o superior:

```sh
python -m unittest discover -s tests -v
python scripts/check_docs.py
python -m gfactory.plan examples/clip-plan.json
```

CI ejecuta el contrato en Python 3.12 y 3.14 y comprueba formato con Ruff 0.15.6. No necesita credenciales ni FFmpeg. La revisión de enlaces es local y no verifica URLs remotas ni anchors.
