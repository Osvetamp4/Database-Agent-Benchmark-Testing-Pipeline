# Database-Agent-Benchmark-Testing-Pipeline


IMPORTANT:

Framework_handler only handles creation of the generic framework. Passes on neccesary credentials and information ot a seperate redis container which manages the frameworks that way.

A seperate eval container can query the redis container to get information on the framework containers themselves.