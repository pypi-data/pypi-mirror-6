import fanstatic


library = fanstatic.Library('mochikit', 'resources')


Base = fanstatic.Resource(
    library, 'Base.js', minified='Base.min.js')
DOM = fanstatic.Resource(
    library, 'DOM.js', minified='DOM.min.js',
    depends=[Base])
Iter = fanstatic.Resource(
    library, 'Iter.js', minified='Iter.min.js',
    depends=[Base])
Style = fanstatic.Resource(
    library, 'Style.js', minified='Style.min.js',
    depends=[Base, DOM])

Async = fanstatic.Resource(
    library, 'Async.js', minified='Async.min.js',
    depends=[Base])
Format = fanstatic.Resource(
    library, 'Format.js', minified='Format.min.js',
    depends=[Base])
DateTime = fanstatic.Resource(
    library, 'DateTime.js', minified='DateTime.min.js',
    depends=[Base])
Logging = fanstatic.Resource(
    library, 'Logging.js', minified='Logging.min.js',
    depends=[Base])
LoggingPane = fanstatic.Resource(
    library, 'LoggingPane.js', minified='LoggingPane.min.js',
    depends=[Base, Logging])
Test = fanstatic.Resource(
    library, 'Test.js', minified='Test.min.js',
    depends=[Base])
MockDOM = fanstatic.Resource(
    library, 'MockDOM.js', minified='MockDOM.min.js')


Selector = fanstatic.Resource(
    library, 'Selector.js', minified='Selector.min.js',
    depends=[Base, DOM, Iter])
Color = fanstatic.Resource(
    library, 'Color.js', minified='Color.min.js',
    depends=[Base, DOM, Style])
Position = fanstatic.Resource(
    library, 'Position.js', minified='Position.min.js',
    depends=[Base, DOM, Style])
Signal = fanstatic.Resource(
    library, 'Signal.js', minified='Signal.min.js',
    depends=[Base, DOM, Style])


Visual = fanstatic.Resource(
    library, 'Visual.js', minified='Visual.min.js',
    depends=[Base, DOM, Style, Color, Position])
DragAndDrop = fanstatic.Resource(
    library, 'DragAndDrop.js', minified='DragAndDrop.min.js',
    depends=[Base, Iter, DOM, Signal, Visual, Position])
Sortable = fanstatic.Resource(
    library, 'Sortable.js', minified='Sortable.min.js',
    depends=[Base, Iter, DOM, Position, DragAndDrop])


mochikit = fanstatic.Group([
    Async,
    Base,
    Color,
    DateTime,
    DOM,
    DragAndDrop,
    Format,
    Iter,
    Logging,
    LoggingPane,
    MockDOM,
    Position,
    Selector,
    Signal,
    Sortable,
    Style,
    Test,
    Visual,
])
