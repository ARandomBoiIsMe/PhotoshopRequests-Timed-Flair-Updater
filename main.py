from utils import config_util, reddit_util
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

CONFIG = config_util.load_config()
REDDIT = reddit_util.initialize_reddit(CONFIG)

THREAD_LOCK = threading.Lock()

# Checks if subreddit exists.
def validate_subreddit(subreddit_name: str):
    if subreddit_name.strip() == '' or subreddit_name is None:
        return None
    
    try:
        return REDDIT.subreddits.search_by_name(subreddit_name, exact=True)[0]
    except prawcore.exceptions.NotFound:
        return None
    
def process_new_post(post: models.Submission):    
    flair_ids_to_trigger_code_logic = ['b730352e-5ace-11ee-bf0d-9e7c5190d2d0',
                                    'c1955a9e-5ace-11ee-acc1-ce042fb18b89',
                                    'ca493cfa-5ace-11ee-bbe5-26d464526c47',
                                    'dadc72c6-5ace-11ee-bb35-7e9b42ca2926']
    
    # Flair IDs to be applied based on how long the respective timers were
    # set to.
    start_timer_flair_id = '07fdad48-5de4-11ee-9876-2e9c1667800a'
    short_timer_flair_id = 'd77946ce-566c-11ee-bea9-76fa97ad0426'
    medium_timer_flair_id = '4976c78e-566c-11ee-a694-ee0751b6e588'
    long_timer_flair_id = '1eb6c630-535a-11ee-92a7-4af16e60d54a'

    try:
        if post.link_flair_template_id not in flair_ids_to_trigger_code_logic:
            return

        # Finally optimized the damn threads.
        print(f"New post to be processed: '{post.title}'")
        if post.link_flair_template_id == 'b730352e-5ace-11ee-bf0d-9e7c5190d2d0':
            time_to_flair_map = {
                1: start_timer_flair_id,
                25: short_timer_flair_id,
                50: medium_timer_flair_id,
                75: long_timer_flair_id
            }

            threading.Thread(target=update_flair_after_X_minutes, args=(post, time_to_flair_map)).start()
        elif post.link_flair_template_id == 'c1955a9e-5ace-11ee-acc1-ce042fb18b89':
            time_to_flair_map = {
                1: start_timer_flair_id,
                50: short_timer_flair_id,
                75: medium_timer_flair_id
            }

            threading.Thread(target=update_flair_after_X_minutes, args=(post, time_to_flair_map)).start()
        elif post.link_flair_template_id == 'ca493cfa-5ace-11ee-bbe5-26d464526c47':
            time_to_flair_map = {
                1: start_timer_flair_id,
                75: short_timer_flair_id,
                100: medium_timer_flair_id
            }

            threading.Thread(target=update_flair_after_X_minutes, args=(post, time_to_flair_map)).start()
        elif post.link_flair_template_id == 'dadc72c6-5ace-11ee-bb35-7e9b42ca2926':
            time_to_flair_map = {
                1: start_timer_flair_id,
                100: short_timer_flair_id
            }

            threading.Thread(target=update_flair_after_X_minutes, args=(post, time_to_flair_map)).start()
    except AttributeError:
        return

def update_flair_after_X_minutes(post: models.Submission, time_to_flair_map: dict()):
    # Gets the index of the current key-value pair in the dictionary.
    for index, (duration, new_flair_id) in enumerate(time_to_flair_map.items()):

        # Calculates how much longer the thread has to sleep to
        # update the flairs accordingly.
        current_duration = 0
        if index == 0:
            current_duration = duration
        else:
            current_duration = duration - list(time_to_flair_map.keys())[index - 1]

        time.sleep(current_duration * 60)
        
        try:
            # Only one thread can update a post flair at any time.
            with THREAD_LOCK:
                post.mod.flair(flair_template_id=new_flair_id)

            print(f"Post flair has been updated after '{duration}' minute(s) - '{post.title}' ")
            logging.info(f"Successfully updated the flair of the post titled '{post.title}' after '{duration}' minute(s)")
        except Exception as e:
            logging.error(f"Failed to update the flair of the post titled '{post.title}' after '{duration}' minute(s). Error: {e}")
            print(f"Error: {e}")

if __name__ == '__main__':
    subreddit_name = CONFIG['VARS']['SUBREDDIT']
    subreddit = validate_subreddit(subreddit_name)
    if not subreddit:
        logging.error(f"Subreddit does not exist: r/{subreddit_name}.")
        print(f"Subreddit does not exist: r/{subreddit_name}.")
        exit()

    if not subreddit.user_is_moderator:
        logging.error(f"You must be a mod in this sub: r/{subreddit_name}.")
        print(f"You must be a mod in this sub: r/{subreddit_name}.")
        exit()

    print("Bot is now running...")
    logging.info("Bot has started running.")
    for post in subreddit.stream.submissions(skip_existing=True):
        process_new_post(post)