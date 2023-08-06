hotdate
=======

`hotdate` is a library for doing friendly date formating. Its API is inspired by [Moment.js](http://momentjs.com).

`hotdate` wraps Python's builtin `datetime` object with a layer that simplifies some common operations that are annoying to do with `datetime`. More importantly, `hotdate` provides functionality for doing friendly/human-readable relative date formatting. It even has one of those crazy "fluent interfaces" that are so hip with the kids these days.

## A quick tour


### Construction

You can create hotdate objects in a bunch of ways.

```python
    from hotdate import hotdate

    # get the current time and date
    >>> hotdate()
    hotdate(2014, 3, 4, 21, 34, 3, 661600)
```

```python
    >>> hotdate(2011)
    hotdate(2011, 1, 1, 0, 0)
```

```python
    >>> hotdate('2012 03', '%Y %m')
    hotdate(2012, 3, 1, 0, 0)
```

```python
    >>> d = datetime.datetime.now()
    >>> hotdate(d)
    hotdate(2014, 3, 4, 21, 34, 3, 661600)
```

### Formatting

You can use it to format dates:


```python

	>>> hotdate().format()
	'2014-03-04T21:46:18'
```

```python
	
	>>> hotdate().format('%c')
	'Tue Mar  4 21:47:03 2014'
```

### "How long ago?"

```python

	>>> hotdate().from_now()
	'just now'
```

```python
	>>> hotdate(2011).from_now()
	'2 years ago'
```

```python
	>>> hotdate().add(minutes=30).from_now()
	'29 minutes from now'
```

### Calendar date formatting

```python

	>>> hotdate().calendar()
	'Today at 09:50PM'
```

```python
	>>> hotdate().add(days=1).calendar()
	'Tomorrow at 09:51PM'
```

```python
	>>> hotdate().subtract(days=4).calendar()
	'Last Friday at 09:51PM'
```

```python
	>>> hotdate(2011).calendar()
	'1/1/2011'
```
