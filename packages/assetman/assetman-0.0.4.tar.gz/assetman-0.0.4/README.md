# Assetman

[![Latest Version](https://pypip.in/v/assetman/badge.png)](https://pypi.python.org/pypi/assetman/)
[![Build Status](https://travis-ci.org/petermelias/assetman.png?branch=master)](https://travis-ci.org/petermelias/assetman)
[![Montly Downloads](https://pypip.in/d/assetman/badge.png?month)](https://pypi.python.org/pypi/assetman)
[![Download format](https://pypip.in/format/assetman/badge.png)](https://pypi.python.org/pypi/assetman/)
[![Coverage Status](https://coveralls.io/repos/petermelias/assetman/badge.png?branch=master)](https://coveralls.io/r/petermelias/assetman?branch=master)
[![License](https://pypip.in/license/assetman/badge.png)](https://pypi.python.org/pypi/assetman/)


## Usage
```python
from assetman import (
	init, 
	create_blob
)

manager = init(aws_key, aws_secret, my_bucket)
some_data = 'my awsome string / image binary / html / markdown / national secrets'
asset = create_blob(some_data)
asset.public = True # makes the asset publicly accessible over S3
manager.save_asset(asset)

print asset.uuid # returns a 16 character UUID which you can save for later

# ... somewhere over the Mediterranean sea...

my_saved_asset = manager.get_asset(uuid)

print my_saved_asset.data
'my awsome string / image binary / html / markdown / national secrets'
```

It is also important to note that there are some convenience Asset Types built in for convenient handling
of meta data and mimetypes.

For example, the ```Image``` asset type will track format and dimensions for you. See tests for example.

## Testing

To install with testing support: ``` pip install -e .[test] ```
This will install with the optional dependencies required for testing. (wand, for example.)
``` nosetests ```