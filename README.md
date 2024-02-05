# Solara pages for SDSS

This package maintains a set of SDSS web pages, applications, or dashboards built with
the [Solara](https://solara.dev/) package.  These applets are designed to be integrated
with the SDSS [Zora](https://github.com/sdss/zora) and [Valis](https://github.com/sdss/valis) applications.  While they can be run indepedently with the ``solara`` server, they may not function fully in their capacity.


## Developer Installation
It is recommended to set this package up within a virtual environment, like pyenv
or conda.

Checkout the repo and install the package in editable mode
```
git clone https://github.com/sdss/sdss_solara.git
cd sdss_solara
pip install -e .
```

This package currently requires a custom fork of the `specutils` package. For now,
you must install this separately with the following:
```
pip install specutils@git+https://github.com/rileythai/specutils-sdss-loaders.git#egg=sdss-v-loaders
```


## License

This project is Copyright (c) Brian Cherinka and licensed under
the terms of the BSD 3-Clause license. This package is based upon
the [Openastronomy packaging guide](https://github.com/OpenAstronomy/packaging-guide)
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

## Contributing

We love contributions! sdss_solara is open source,
built on open source, and we'd love to have you hang out in our community.

**Imposter syndrome disclaimer**: We want your help. No, really.

There may be a little voice inside your head that is telling you that you're not
ready to be an open source contributor; that your skills aren't nearly good
enough to contribute. What could you possibly offer a project like this one?

We assure you - the little voice in your head is wrong. If you can write code at
all, you can contribute code to open source. Contributing to open source
projects is a fantastic way to advance one's coding skills. Writing perfect code
isn't the measure of a good developer (that would disqualify all of us!); it's
trying to create something, making mistakes, and learning from those
mistakes. That's how we all improve, and we are happy to help others learn.

Being an open source contributor doesn't just mean writing code, either. You can
help out by writing documentation, tests, or even giving feedback about the
project (and yes - that includes giving feedback about the contribution
process). Some of these contributions may be the most valuable to the project as
a whole, because you're coming to the project with fresh eyes, so you can see
the errors and assumptions that seasoned contributors have glossed over.

Note: This disclaimer was originally written by
[Adrienne Lowe](https://github.com/adriennefriend) for a
[PyCon talk](https://www.youtube.com/watch?v=6Uj746j9Heo), and was adapted by
sdss_solara based on its use in the README file for the
[MetPy project](https://github.com/Unidata/MetPy).
