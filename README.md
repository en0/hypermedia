# Hypermedia Wrapper #

An attempt at a jsonhal / hypermedia wrapper.

---

## Goals ##

The goals of this project are to achive the following:

1. Enforce entity consistancy of a RESTful API by using project defeined representations of data.
2. Automate rendering of hypermedia content on those representations
3. Create a simple and flexable model for use with flask-RESTful uwsgi module.
4. Create a simple and flexable interface between the hypermedia wrappers and sqlalchemy models
5. Support versioning of representations as a native function of the API within the hypermedia module.
6. Learn new things and write cool code.

## Some notes ##

If a content type is not available for a specfic representation, the proper code is:

```
500 - Unsupported Content-Type: {content-type}; supported ones are: {Supported content-types}
```

## Refrences ##
(JsonHAL)[http://stateless.co/hal_specification.html]
(Haltalk)[http://haltalk.herokuapp.com/explorer/browser.html#/]
