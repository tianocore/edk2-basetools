# Unit testing of vfrcompiler

## Pytest
- install: pip install pytest

## Run test
- cd edk2\BaseTools\Source\Python\tests
- open pytest.ini and Modify the parameters that need to be used
```
python_files =
    # test_split.py
    test_Vfrcompiler.py

This parameter selects the test file.
```

- run pytest in cmd