import time

from datetime import datetime

def update_post_relations(user, topic, deleting=False):
    """
    helper function to update user post count and parent topic post_count.
    """
    if deleting:
        user.post_count = user.post_count - 1
    else:
        user.post_count += 1
    user.save(update_fields=['post_count'])

    topic.modified     = datetime.now()
    topic.modified_int = time.time()
    topic.save(update_fields=['modified', 'modified_int'])
