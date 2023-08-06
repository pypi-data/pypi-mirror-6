from pymongo import MongoClient


def get_total_size(db_name):
    client = MongoClient()
    db = client[db_name]
    total_objects = 0
    total_size = 0
    apps = db.apps.find()
    for app in apps:
        classes = app['classes']
        for cls in classes:
            stats = db.command('collStats', cls)
            total_objects += stats['count']
            total_size += stats['storageSize']

    return total_objects, total_size
