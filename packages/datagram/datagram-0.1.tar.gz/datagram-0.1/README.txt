This is a small package with some functions that help me to handle data
in a fast and easier way. The main goal is to fit data without making
a mess.

Although of course there's nothing new here, the classes Histogram and
Distribution here present seem to me nicer to work with in comparison 
with other frameworks. These two classes are the core of the package.

Class Histogram allows fast generation of pdfs and cdfs, while data can
be added to the object at any time. The package is thought for discrete
data, usually sparse, so it is stored in a dictionary.

Class Distribution is a wrapper of distribution functions (pdf, cdf,
likelihood, etc.) which is a counterpart of Histogram, used in the fitting
process.

Copyright 2013 Jose Maria Miotto