# Meetup RSVP stream listener
___



The service will connect to the Meetup Long-Polling RSVP stream ([Meetup Long-Polling RSVP Stream](http://stream.meetup.com/2/rsvps)) and stores the information acquired on a RDBMS database in MariaDb [linuxserver/mariadb:latest](https://hub.docker.com/r/linuxserver/mariadb)



---
#### `1. get_chunk_size`
The below function will return an integer with the size in bytes of a stream chunk.
```python
get_chunk_size()
```
Get the size of a complete event from the stream.
`:param: none`
`:return: int` _length of a complete event, in bytes_
#### `2. get_chunk_data`
Return a chunk from the stream of chunk_size bytes.
```python
get_chunk_data(chunk_size)
```
Get the 'chunk_size' bytes from the stream
`:param: chunk_size`: _http stream data_
`:return: str`: _return a chunk from the stream of `chunk_size` bytes_

#### `3. iter_listen`
The below is a generator function, yielding rsvp events from the stream, as formatted **JSON** strings.

```python
iter_listen()
```

`:param: none`
`:return: json string`

#### `4. listen()`
When invoked, this function will start collecting data from the RSVP stream, will filter the portion of data of interest, and make it persistent on the `meetup->cities` table.
```python
listen()
```
`:param: none`

#### `5. create_table`
This function will drop the cities table (if exists), and create a new empty table.
```python
create_table()
```
`:param: none`
#### `6. filter_data`
Within this function we setup the filter in use by the listen() function. It will take the rsvp event JSON string, and return a JSON string subset of that data.
```python
filter_data(data)
```

`:param: json string`
`:return: json string`

#### `7. database schema`

```
CREATE TABLE `cities` (
  `idx` int(11) NOT NULL AUTO_INCREMENT,
  `city` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `lat` float(5,2) DEFAULT NULL,
  `lon` float(5,2) DEFAULT NULL,
  `date` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `eid` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `gid` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `mid` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`idx`)
) ENGINE=InnoDB AUTO_INCREMENT=47322 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
```
