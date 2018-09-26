Things
======

> Things. Just Things...

### System requirements

```bash
python --version >= 3.6
```

### Dependencies

Don't forget activate virtualenv:
```bash
pip install -r requirements.txt
```

### Testing

Run all tests:
```bash
pytest -sv things/tests.py
```

### Run development server

```bash
export FLASK_APP=things FLASK_ENV=development FLASK_DEBUG=1
flask run
```
