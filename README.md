# GenericWebScrapper

This is a generic scrapper target to scrape any webpage with ease.

How to use it:

1. put down your table name as the section in the config/dataFormat.ini
2. put down all your targeted element and its xpath as key-value pair under the sections
3. Customize your own UrlGenerator which helps to yield different targeted url and primary key
4. If neeeded, customized your own logic by inheriting and overriding the GenericScrapper Class 
5. Start the program and it will scrape each url yielded from the UrlGenerator and write one row into the database




race_dividend
maatch_info
win_result
