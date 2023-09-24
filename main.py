from utils import config_util, reddit_util, database_util
import logging
import prawcore
import time
import threading
from praw import models

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="run.log"
)

connection = database_util.connect_to_db()
config = config_util.load_config()
reddit = reddit_util.initialize_reddit(config)

def main():
    subreddit_name = config['VARS']['SUBREDDIT']
    subreddit = validate_subreddit(subreddit_name)
    if not subreddit:
        logging.error(f"Subreddit does not exist: r/{subreddit_name}.")
        print(f"Subreddit does not exist: r/{subreddit_name}.")
        exit()

    if not subreddit.user_is_moderator:
        logging.error(f"You must be a mod in this sub: r/{subreddit_name}.")
        print(f"You must be a mod in this sub: r/{subreddit_name}.")
        exit()

    posts = get_newest_posts_since_last_run(subreddit)
    threads = []
    flair_ids_to_trigger_code_logic = ['b730352e-5ace-11ee-bf0d-9e7c5190d2d0',
                                    'c1955a9e-5ace-11ee-acc1-ce042fb18b89',
                                    'ca493cfa-5ace-11ee-bbe5-26d464526c47',
                                    'dadc72c6-5ace-11ee-bb35-7e9b42ca2926']
    
    # Flair IDs to be applied based on how long the respective timers were
    # set to.
    short_timer_flair_id = 'd77946ce-566c-11ee-bea9-76fa97ad0426'
    medium_timer_flair_id = '4976c78e-566c-11ee-a694-ee0751b6e588'
    long_timer_flair_id = '1eb6c630-535a-11ee-92a7-4af16e60d54a'
    for post in posts:
        try:
            if post.link_flair_template_id not in flair_ids_to_trigger_code_logic:
                continue

            # Creates multiple timers in separate threads to ensure that they all
            # count down separately. I'll try to optimize this later, because the
            # idea of multiple threads running like that kind of annoys me.
            if post.link_flair_template_id == 'b730352e-5ace-11ee-bf0d-9e7c5190d2d0':
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(25, post, short_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(50, post, medium_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(75, post, long_timer_flair_id)))
            elif post.link_flair_template_id == 'c1955a9e-5ace-11ee-acc1-ce042fb18b89':
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(50, post, short_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(75, post, medium_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(100, post, long_timer_flair_id)))
            elif post.link_flair_template_id == 'ca493cfa-5ace-11ee-bbe5-26d464526c47':
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(75, post, short_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(100, post, medium_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(125, post, long_timer_flair_id)))
            elif post.link_flair_template_id == 'dadc72c6-5ace-11ee-bb35-7e9b42ca2926':
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(100, post, short_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(125, post, medium_timer_flair_id)))
                threads.append(threading.Thread(target=update_flair_after_X_minutes_pass, args=(150, post, long_timer_flair_id)))
        except AttributeError:
            continue

    # Starts all timers in their respective threads.
    for thread in threads:
        thread.start()

    # Waits for all threads to finish executing before continuing the program.
    for thread in threads:
        thread.join()

    # Because the first post in the posts list is also the most recent
    # post, I can directly take its creation time and store it for later.
    if len(posts) != 0:
        database_util.insert_time(connection, posts[0].created_utc)

    database_util.close_connection(connection)

    logging.info("All flairs have been updated successfully.")

# Checks if subreddit exists.
def validate_subreddit(subreddit_name: str):
    if subreddit_name.strip() == '' or subreddit_name is None:
        return None
    
    try:
        return reddit.subreddits.search_by_name(subreddit_name, exact=True)[0]
    except prawcore.exceptions.NotFound:
        return None

# Filters out posts that are older than the last visited post
# from the last run.
def get_newest_posts_since_last_run(subreddit: models.Subreddit):
    posts = subreddit.new(limit=None)

    time_of_last_visited_post = database_util.retrieve_time(connection)

    # This only happens when the script is being run for the first time.
    if not time_of_last_visited_post:
        logging.info("Successfully retrieved the new posts in the subreddit.")
        return list(posts)

    newest_posts = []
    for post in posts:
        if (post.created_utc > time_of_last_visited_post[0]):
            newest_posts.append(post)
        else:
            break
    
    logging.info("Successfully retrieved the newest posts since the last run.")
    return newest_posts
    
def update_flair_after_X_minutes_pass(duration: int, post: models.Submission, new_flair_id: str):
    logging.info(f"The flair of the post titled '{post.title}' will be updated after '{duration}' minute(s)")
    time.sleep(duration * 60) # Multiply duration by 60 to wait in minutes.
    
    post.mod.flair(flair_template_id=new_flair_id) # Sets the new flair.
    logging.info(f"Successfully updated the flair of the post titled '{post.title}' after '{duration}' minute(s)")

    time.sleep(1) # Idk I just like how this looks.

if __name__ == '__main__':
    main()