

<img src="https://i.imgur.com/V1ONURi.png?1" title="Scraper" alt="Scraper">

# Craiglist Scraper

Craiglist Scraper was created to help find new listings on Craiglist. 
The tool is designed to run using Flask. Input your criteria, and hit run. The scraper will continously scan for new listings, and email you when new listings are posted.

## Installation

 - Download files

```shell
$ pip install -r requirements.txt
```
- Run crawler.py 

**NOTE** - This will run in a development server. To upload, you will need to use asynchronous task queues such as Celery. See Miguel Grinbergs post [here](https://blog.miguelgrinberg.com/post/using-celery-with-flask)

## Usage

- Fill out form.
- Run the program (must be left open).

## Contributing
Pull requests are welcome


## License
[MIT](https://choosealicense.com/licenses/mit/)
