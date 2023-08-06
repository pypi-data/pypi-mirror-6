import redis
import json
import os

class KeyStore:
  
  def get_value(key, attribute):
    return NotImplemented

  def set_value(key, attribute, value):
    return NotImplemented

  def dump():
    return NotImplemented

  def restore(data):
    return NotImplemented


class RedisStore(KeyStore):

  def __init__(self):
    redis_db = 5
    self.connection = redis.Redis(host='localhost', port=6379, db=redis_db)

  def get_value(self, key, attribute):
    return self.connection.hget(key, attribute)

  def set_value(self, key, attribute, value):
    self.connection.hset(key, attribute, value)

  def restore(self, data):
    for key in data:
      self.connection.hmset(key, data[key])


class JSONStore(KeyStore):

  def __init__(self, store_filename='store.json'):
    self.store_filename = store_filename
    if not os.path.exists(store_filename):
      f = open(store_filename, 'w')
      f.write('{}')
      f.close()

  def __read_store(self):
    raw_data = open(self.store_filename, 'r')
    data = json.load(raw_data)
    raw_data.close()
    return data

  def __write_store(self, data):
    json_file = open(self.store_filename, 'w')
    json_file.write(json.dumps(data))
    json_file.close()

  def dump(self):
    return self.__read_store()

  def restore(self, data):
    self.__write_store(data)

  def get_value(self, key, attribute):
    try:
      value = self.__read_store()[key][attribute]
    except KeyError:
      value = None
    return value

  def set_value(self, key, attribute, value):
    print key
    print attribute
    print value
    json_data = self.__read_store()
    if not key in json_data:
      json_data[key] = {attribute: value}
    else:
      json_data[key][attribute] = value
    self.__write_store(json_data)


def new_store(driver):
  if driver == 'redis':
    return RedisStore()
  elif driver == 'json':
    return JSONStore()
  else:
    raise Exception("Driver %s not supported" % driver)
