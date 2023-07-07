# vimeotools
These are Python Tools for Vimeo, using the Vimeo API and the official PyVimeo Python package.

This package is aimed at being more convenient than using the Vimeo API or PyVimeo directly:
it provides the **VimeoConnection**, **VimeoVideo**; **VimeoShowcase** (Album) and **VimeoFolder** (project) classes which invoke the API for you. So you don't have to worry about the intricacies of the data structure or the URIs to use for specific queries or actions.

These classes also store the data internally once they have retrieved them from Vimeo, so as to avoid unnecessary requests. If an instance changes data, the internal data representation is updated accordingly. Of course these changes made can render other object's internal data obsolete, so they may have to be updated using their *refresh* method.

You can also opt to create or set an object in live mode, so everytime a property is queried, the appropriate request is made on Vimeo first.
