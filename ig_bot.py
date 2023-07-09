from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import configparser
import datetime
import time

s = Service("C:\\chromedriver.exe")
opt = Options()
opt.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(service=s, options=opt)

driver.get("http://google.com")
wait = WebDriverWait(driver, 10)

###################################
# STEP 1 - CREATE IG FOLLOWERS LIST
###################################


# Click home button icon
def click_home_button():
    home = driver.find_element(By.XPATH, "//div[@class='_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _abcj _abcm']//*"
                                         "[@aria-label='Home']")

    home.click()


# Maximize window and go to URL
def max_win_get_url():
    driver.maximize_window()
    driver.get("http://instagram.com")


# Enters in login details
def enter_login_details():
    config = configparser.ConfigParser()
    config.read('C:\\Users\\garre\\PycharmProjects\\IG Bot\\ig_login_credentials.ini')
    username = config['credentials']['username']
    password = config['credentials']['password']
    user_name = driver.find_element(By.NAME, 'username')
    user_name.clear()
    user_name.send_keys(username)
    pass_word = driver.find_element(By.NAME, 'password')
    pass_word.clear()
    pass_word.send_keys(password)


# Log in
def log_in():
    login_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Log in')]")
    login_button.click()


# Bypass pop-ups
def bypass_popups():
    wait.until(ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Not Now')]")))
    save_info_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Not Now')]")
    save_info_button.click()
    time.sleep(10)
    wait.until(ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Not Now')]")))
    turn_on_notif_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Not Now')]")
    turn_on_notif_button.click()


# Search for Specific Profile
def search_for_profile():
    # Access Search bar
    search_icon = driver.find_element(By.XPATH, "//*[contains(text(), 'Search')]")
    search_icon.click()
    time.sleep(5)
    search_input = driver.find_element(By.CLASS_NAME, '_aauy')
    time.sleep(5)
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CLASS_NAME, '_aauy')))

    # Search for Specific Profile
    search_input.send_keys('')  # << ENTER INSTAGRAM PROFILE HANDLE TO SCRAPE FOLLOWERS FROM
    time.sleep(5)
    profile_selection = driver.find_element(By.XPATH, "//*[contains(text(), '')]")  # << ENTER IG PROFILE HANDLE AGAIN
    profile_selection.click()


# Add Profile Followers to raw_ig_followers_list.txt
def create_followers_list():
    # Access The Profile Followers (from previous section)
    # profile_followers = driver.find_element(By.XPATH, "//*[contains(text(), ' followers')]")
    # profile_followers.click()

    # Scroll to bottom of followers list using javascript
    time.sleep(1)
    scroll_path = '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]'
    # WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, scroll_path)))
    scroll_box = driver.find_element(By.XPATH, scroll_path)

    # Scroll through all followers in chunks of 100
    chunk_size = 100
    last_ht, ht = 0, 1
    while True:
        last_ht = ht
        time.sleep(1)
        ht = driver.execute_script("""
        arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;""", scroll_box)
        if last_ht == ht:
            break

        if not driver.execute_script("return arguments[0].parentNode", scroll_box):
            break

        # Find all the links within the scrollable element
        links = scroll_box.find_elements(By.TAG_NAME, "a")

        # Create a new list with unique elements
        unique_links = []

        # Iterate over the list of links
        for link in links:
            # Get the href attribute of the link
            href = link.get_attribute("href")

            # Check the number of times the href attribute appears in the list
            count = unique_links.count(href)

            # If the href attribute does not appear in the list, add it
            if count == 0:
                unique_links.append(href)
            # If the href attribute appears in the list, remove the duplicate elements
            elif count > 1:
                while unique_links.count(href) > 1:
                    unique_links.remove(href)

        # Open a text file for writing
        with open("raw_ig_followers_list.txt", "w") as file:
            # Iterate over the list of unique links
            for link in unique_links:
                # Write the href attribute to the text file
                file.write(link + "\n")

        # Break the loop if the number of links processed is equal to the chunk size
        if len(unique_links) == chunk_size:
            break

#######################################################
# STEP 2 - CLEAN FOLLOWERS LIST BY REMOVING EVERYTHING
#######################################################


# Remove hrefs from raw_list and create new list username_list.txt to just show usernames
def create_username_list():
    with open('raw_ig_followers_list.txt', 'r') as input_file, open('username_list.txt', 'w') as output_file:
        for line in input_file:
            modified_line = line.replace('https://www.instagram.com', '')
            modified_line = modified_line.replace('/', '')
            output_file.write(modified_line)


def remove_male_names():
    with open('username_list.txt', 'r') as f:
        usernames = f.read().splitlines()

    with open('male_names.txt', 'r') as f:
        male_names = f.read().splitlines()

    male_names = [x.lower() for x in male_names]
    usernames = [x.lower() for x in usernames]

    for username in usernames:
        for male_name in male_names:
            usernames[:] = [x for x in usernames if male_name not in x]

    with open("username_list.txt", "w") as f:
        f.writelines("\n".join(usernames))


def remove_duplicates():
    # Read the contents of the file
    with open("username_list.txt", "r") as f:
        usernames = f.read().splitlines()
    # create a new list of usernames, containing the unique usernames
    filtered_usernames = [username for i, username in enumerate(usernames) if username not in usernames[:i]]

    # Open the file in write mode and write the updated list of usernames to it
    with open("username_list.txt", "w") as f:
        f.writelines("\n".join(filtered_usernames))

    print('Done')


def remove_disqualified_words():
    with open('username_list.txt', 'r') as f:
        usernames = f.read().splitlines()

    with open('disqualified_words.txt', 'r') as f:
        words = f.read().splitlines()

    words = [x.lower() for x in words]
    usernames = [x.lower() for x in usernames]

    for username in usernames:
        for word in words:
            usernames[:] = [x for x in usernames if word not in x]

    with open("username_list.txt", "w") as f:
        f.writelines("\n".join(usernames))


def remove_disqualified_usernames():
    # STEP 1 - Access the username_list.txt
    with open("username_list.txt", "r") as f:
        lines = f.readlines()

    # Remove the leading and trailing whitespace from each line
    usernames = [line.strip() for line in lines]

    # Make a copy of the usernames to be iterated over, so that the original list is not modified
    usernames_copy = usernames.copy()

    # Complete username List
    completed_usernames = []

    # Initialize counter to know when we have completed the steps below for the specified amount
    good_counter = 0
    bad_counter = 0
    total_counter = 0

    # Get end time
    start_time = datetime.datetime.now().strftime("%I:%M %p")

    # STEP 2 - Search for profile and like their posts
    for username in usernames_copy:
        # SEARCH FOR USERNAME & CLICK INTO THEIR PROFILE
        print(f"Executing tasks for username: {username}")

        # Click Home Button
        click_home_button()

        # Find Search Icon Element
        search_icon = wait.until(
            ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Search')]")))
        time.sleep(1)

        try:
            # Click on Search Icon
            search_icon.click()
        except StaleElementReferenceException:
            # Relocate the search icon
            search_icon = wait.until(
                ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Search')]")))
            time.sleep(1)

            # Click on Search Icon
            search_icon.click()

        # Find Search Bar
        search_bar = wait.until(
            ec.presence_of_element_located((By.CLASS_NAME, '_aauy')))
        time.sleep(2)

        try:
            # Click on the Search Bar
            search_bar.clear()
            search_bar.click()

        except StaleElementReferenceException:
            # Relocate Search Bar
            search_bar = wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, '_aauy')))
            time.sleep(2)

            # Click on the Search Bar
            search_bar.clear()
            search_bar.click()

        # Enter username into search bar
        search_bar.send_keys(f'{username}')

        try:
            # Find username in search result and click into their profile
            profile_selection = wait.until(
                ec.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{username}')]")))
            time.sleep(5)
            profile_selection.click()

            # Wait for page to load
            time.sleep(5)

            print(f"Checking profile: {username}")
            try:
                posts_element = driver.find_element(By.XPATH, '//div[@class="_ab8w  _ab94 _ab97 _ab9f _ab9k _ab9p '
                                                              '_abcm"]//*[text()="Posts"]')
                time.sleep(5)
                posts_element.click()

                # Check if profile has available posts
                elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/p/']")[:5]
                time.sleep(5)

                # Add 1 to counter
                good_counter += 1
                total_counter += 1

                # Add username to completed_usernames
                completed_usernames.append(username)
                print(f'Adding {username} to completed usernames')

                # Add the updated list of usernames to completed list
                print('Rewriting complete_username_list.txt')
                with open("complete_username_list.txt", "a") as f:
                    for username in completed_usernames:
                        f.write(username + "\n")
                completed_usernames = []  # clearing the list

                # Remove username from usernames list
                usernames.remove(username)
                print(f'Removing {username} from usernames')

                # Write the updated list of usernames to the file
                print('Rewriting username_list.txt')
                with open("username_list.txt", "w") as f:
                    for username in usernames:
                        f.write(username + "\n")

                # Print number of profiles completed
                print(f'Total Accounts Checked: {total_counter}')
                print(f'Disqualified Accounts: {bad_counter}')
                print(f'Accounts Added to Completed List: {good_counter}')

                if total_counter == 20:

                    # Get end time
                    end_time = datetime.datetime.now().strftime("%I:%M %p")
                    # Print time details
                    print("Start Time: ", start_time)
                    print("End Time: ", end_time)
                    break

            except NoSuchElementException:
                print(f'No posts found for username: {username}')

                # Remove username from usernames list
                usernames.remove(username)
                print(f'Removing {username} from usernames')

                # Write the updated list of usernames to the file
                print('Rewriting username_list.txt')
                with open("username_list.txt", "w") as f:
                    for username in usernames:
                        f.write(username + "\n")

                # Add 1 to counters
                bad_counter += 1
                total_counter += 1

                # Print number of profiles completed
                print(f'Total Accounts Checked: {total_counter}')
                print(f'Disqualified Accounts: {bad_counter}')
                print(f'Accounts Added to Completed List: {good_counter}')

                if total_counter == 20:
                    # Get end time
                    end_time = datetime.datetime.now().strftime("%I:%M %p")
                    # Print time details
                    print("Start Time: ", start_time)
                    print("End Time: ", end_time)
                    break

        except NoSuchElementException:
            print(f'{username} not found')

            # Remove username from usernames list
            usernames.remove(username)
            print(f'Removing {username} from usernames')

            # Write the updated list of usernames to the file
            print('Rewriting username_list.txt')
            with open("username_list.txt", "w") as f:
                for username in usernames:
                    f.write(username + "\n")

            # Add 1 to counters
            bad_counter += 1
            total_counter += 1

            # Print number of profiles completed
            print(f'Total Accounts Checked: {total_counter}')
            print(f'Disqualified Accounts: {bad_counter}')
            print(f'Accounts Added to Completed List: {good_counter}')

            if total_counter == 20:
                # Get end time
                end_time = datetime.datetime.now().strftime("%I:%M %p")
                # Print time details
                print("Start Time: ", start_time)
                print("End Time: ", end_time)
                break

        except TimeoutException:
            print(f'{username} not found')

            # Remove username from usernames list
            usernames.remove(username)
            print(f'Removing {username} from usernames')

            # Write the updated list of usernames to the file
            print('Rewriting username_list.txt')
            with open("username_list.txt", "w") as f:
                for username in usernames:
                    f.write(username + "\n")

            # Add 1 to counters
            bad_counter += 1
            total_counter += 1

            # Print number of profiles completed
            print(f'Total Accounts Checked: {total_counter}')
            print(f'Disqualified Accounts: {bad_counter}')
            print(f'Accounts Added to Completed List: {good_counter}')

            if total_counter == 20:
                # Get end time
                end_time = datetime.datetime.now().strftime("%I:%M %p")
                # Print time details
                print("Start Time: ", start_time)
                print("End Time: ", end_time)
                break

#####################################
# STEP 3 - BEGIN LIKING PROFILE POSTS
#####################################


def like_username_posts():
    with open("complete_username_list.txt", "r") as f:
        lines = f.readlines()
    usernames = [line.strip() for line in lines]

    usernames_copy = usernames.copy()

    counter = 0

    liked_accounts = []

    # Get start time of program
    start_time = datetime.datetime.now().strftime("%I:%M %p")

    for username in usernames_copy:
        print('')
        print(f"Executing tasks for username: {username}")

        click_home_button()
        print('Home button clicked')

        search_icon = wait.until(
            ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Search')]")))

        try:
            time.sleep(3)
            search_icon.click()
            print('Search icon located')
        except StaleElementReferenceException:
            # Relocate the search icon
            print('Locating search icon element')
            search_icon = wait.until(
                ec.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Search')]")))
            time.sleep(3)
            search_icon.click()
            print('Search icon located')

        search_bar = wait.until(
            ec.presence_of_element_located((By.CLASS_NAME, '_aauy')))
        time.sleep(3)

        try:
            search_bar.click()
            time.sleep(1)
            search_bar.clear()
            time.sleep(1)
            search_bar.click()
            time.sleep(1)
        except StaleElementReferenceException:
            # Relocate Search Bar
            search_bar = wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, '_aauy')))
            time.sleep(3)

            # Click on the Search Bar
            search_bar.click()
            time.sleep(1)
            search_bar.clear()
            time.sleep(1)
            search_bar.click()
            time.sleep(1)

        print(f'Typing {username} in search bar')
        search_bar.send_keys(f'{username}')
        time.sleep(5)

        try:
            print(f'Locating {username} profile')
            profile = wait.until(
                ec.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{username}')]")))
            print(f'{username} profile located')
            time.sleep(3)
            profile.click()
            print(f'Redirecting to {username} profile')
            time.sleep(3)
            try:
                print(f'Locating {username} profile posts')
                posts_element = wait.until(ec.presence_of_element_located((By.XPATH, '//div[@class="_ab8w  _ab94 '
                                                                                     '_ab97 _ab9f _ab9k _ab9p _abcm"]'
                                                                                     '//*[text()="Posts"]')))
                time.sleep(3)
                print('Posts found')
                posts_element.click()

                try:
                    element1 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/'
                                                             'div[1]/div[2]/section/main/div/div[2]/article/div[1]/div/'
                                                             'div[1]/div[1]')
                    element1.click()
                    print('Clicking into first media post')

                    like_counter = 0
                    time.sleep(3)

                except NoSuchElementException:
                    try:
                        element2 = driver.find_element(By.XPATH,
                                                       '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/'
                                                       'div[2]/section/main/div/div[3]/article/div[1]/div/div[1]/'
                                                       'div[1]/a')
                        element2.click()
                        print('Clicking into first media post')

                        like_counter = 0
                        time.sleep(3)

                    except NoSuchElementException:
                        try:
                            element3 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div/div/div/'
                                                                     'div[1]/div[1]/div[2]/section/main/div/div[2]/'
                                                                     'article/div[1]/div/div[1]/div[1]/a')
                            element3.click()
                            print('Clicking into first media post')

                            like_counter = 0
                            time.sleep(3)

                        except NoSuchElementException:
                            try:
                                element4 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div/'
                                                                         'div/div/div[1]/div[1]/div[2]/section/main/'
                                                                         'div/div[2]/article/div[1]/div/div[1]/'
                                                                         'div[1]/a/div')
                                element4.click()
                                print('Clicking into first media post')

                                like_counter = 0
                                time.sleep(3)

                            except NoSuchElementException:
                                try:
                                    element5 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/'
                                                                             'div/div/div/div[1]/div[1]/div[2]/'
                                                                             'section/main/div/div[2]/article/div[1]/'
                                                                             'div/div[1]/div[1]/a/div/div[2]')

                                    element5.click()
                                    print('Clicking into first media post')

                                    like_counter = 0
                                    time.sleep(3)
                                except NoSuchElementException:
                                    try:
                                        element6 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/'
                                                                                 'div/div/div/div[1]/div[1]/div[2]/'
                                                                                 'section/main/div/div[2]/article/'
                                                                                 'div[1]/div/div[1]/div[1]/a')

                                        element6.click()
                                        print('Clicking into first media post')

                                        like_counter = 0
                                        time.sleep(3)
                                    except NoSuchElementException:
                                        try:
                                            element7 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/'
                                                                                         'div/div[1]/div/div/div/'
                                                                                         'div[1]/div[1]/div[2]/section/'
                                                                                         'main/div/div[2]/article/'
                                                                                         'div[1]/div/div[1]/div[1]/'
                                                                                         'a/div[1]/div[2]')

                                            element7.click()
                                            print('Clicking into first media post')
                                            like_counter = 0
                                            time.sleep(3)
                                        except NoSuchElementException:
                                            print(f'Posts element NOT found for {username}')

                                            usernames.remove(username)
                                            print(f'{username} removed from complete username list')

                                            with open("complete_username_list.txt", "w") as f:
                                                for item in usernames:
                                                    f.write(item + "\n")
                                            print('complete_username_list.txt updated')
                                            continue

                # POST #1
                try:
                    print('Locating heart button')
                    heart_btn = wait.until(
                        ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/'
                                                                  'div[1]/div/div[3]/div/div/div/div/div[2]/div/'
                                                                  'article/div/div[2]/div/div/div[2]/section[1]/'
                                                                  'span[1]/button')))
                    time.sleep(3)
                    print('Heart button located')
                    heart_btn.click()
                    like_counter += 1
                    print(f'Liked post #{like_counter}')

                    # NEXT
                    try:
                        print('Locating Next button')
                        next_btn = driver.find_element(By.XPATH,
                                                       "//div[@class=' _aaqg _aaqh']//*[@aria-label='Next']")
                        next_btn.click()
                        time.sleep(3)

                        # POST #2
                        try:
                            heart_btn = wait.until(
                                ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/'
                                                                          'div/div/div[1]/div/div[3]/div/div/div/'
                                                                          'div/div[2]/div/article/div/div[2]/div/'
                                                                          'div/div[2]/section[1]/span[1]/button')))
                            time.sleep(3)
                            print('Heart button located')
                            heart_btn.click()
                            like_counter += 1
                            print(f'Liked post #{like_counter}')

                            # NEXT
                            try:
                                print('Locating Next button')
                                next_btn = driver.find_element(By.XPATH,
                                                               "//div[@class=' _aaqg _aaqh']//*[@aria-label='Next']")
                                next_btn.click()
                                time.sleep(3)

                                # POST #3
                                try:
                                    heart_btn = wait.until(
                                        ec.presence_of_element_located(
                                            (By.XPATH, '/html/body/div[2]/div/div/div/div[2]/'
                                                       'div/div/div[1]/div/div[3]/div/div/div/'
                                                       'div/div[2]/div/article/div/div[2]/div/'
                                                       'div/div[2]/section[1]/span[1]/button')))
                                    time.sleep(3)
                                    print('Heart button located')
                                    heart_btn.click()
                                    like_counter += 1
                                    print(f'Liked post #{like_counter}')

                                    # NEXT
                                    try:
                                        print('Located Next button')
                                        next_btn = driver.find_element(By.XPATH,
                                                                       "//div[@class=' _aaqg _aaqh']//*[@aria-label='Next']")
                                        next_btn.click()
                                        time.sleep(3)

                                        # POST #4
                                        try:
                                            heart_btn = wait.until(
                                                ec.presence_of_element_located((
                                                    By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/'
                                                              'div/div[3]/div/div/div/div/div[2]/div/article/div/'
                                                              'div[2]/div/div/div[2]/section[1]/span[1]/button')))
                                            time.sleep(3)
                                            heart_btn.click()
                                            like_counter += 1
                                            print(f'Liked post #{like_counter}')

                                            # NEXT
                                            try:
                                                print('Locating Next button')
                                                next_btn = driver.find_element(By.XPATH,
                                                                               "//div[@class=' _aaqg _aaqh']//*[@aria-label='Next']")
                                                next_btn.click()
                                                time.sleep(3)

                                                # POST #5
                                                try:
                                                    heart_btn = wait.until(
                                                        ec.presence_of_element_located((
                                                            By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/'
                                                                      'div/div[1]/div/div[3]/div/div/div/div/'
                                                                      'div[2]/div/article/div/div[2]/div/div/'
                                                                      'div[2]/section[1]/span[1]/button')))
                                                    time.sleep(3)
                                                    heart_btn.click()
                                                    like_counter += 1
                                                    print(f'Liked post #{like_counter}')
                                                    time.sleep(3)

                                                    like_counter = 0
                                                    counter += 1
                                                    liked_accounts.append(username)
                                                    with open("liked_posts_username_list.txt", "a") as f:
                                                        for item in liked_accounts:
                                                            f.write(item + "\n")
                                                    print('liked_posts_username_list.txt updated')

                                                    usernames.remove(username)
                                                    print(f'{username} removed from complete username list')
                                                    with open("complete_username_list.txt", "w") as f:
                                                        for item in usernames:
                                                            f.write(item + "\n")
                                                    print('complete_username_list.txt updated')
                                                    print('')
                                                    print(f'Total Accounts Completed: {counter}')
                                                    print('')

                                                    if counter == 20:
                                                        print('20 accounts completed')

                                                        end_time = datetime.datetime.now().strftime("%I:%M %p")

                                                        print("Start Time: ", start_time)
                                                        print("End Time: ", end_time)

                                                        # Ends the program
                                                        driver.stop_client()
                                                        break

                                                    # CLOSE MEDIA POP UP WINDOW
                                                    try:
                                                        print('Closing media pop-up window')
                                                        close_media = wait.until(
                                                            ec.presence_of_element_located(
                                                                (By.XPATH, '/html/body/div[2]/div/div/'
                                                                           'div/div[2]/div/div/div[1]/'
                                                                           'div/div[2]/div/div')))

                                                        time.sleep(3)
                                                        close_media.click()
                                                        continue
                                                    except NoSuchElementException:
                                                        print('NOT able to close Media Pop-up Window')
                                                        break

                                                except NoSuchElementException:
                                                    print(f'Heart button NOT found for: {username}')

                                                    usernames.remove(username)
                                                    print(f'{username} removed from complete username list')

                                                    with open("complete_username_list.txt", "w") as f:
                                                        for item in usernames:
                                                            f.write(item + "\n")
                                                    print('complete_username_list.txt updated')

                                                    # CLOSE MEDIA POP UP WINDOW
                                                    try:
                                                        print('Closing media pop-up window')
                                                        close_media = wait.until(
                                                            ec.presence_of_element_located(
                                                                (By.XPATH, '/html/body/div[2]/div/div/'
                                                                           'div/div[2]/div/div/div[1]/'
                                                                           'div/div[2]/div/div')))

                                                        time.sleep(3)
                                                        close_media.click()
                                                        continue
                                                    except NoSuchElementException:
                                                        print('NOT able to close Media Pop-up Window')
                                                        break

                                            except NoSuchElementException:
                                                print(f'Next button NOT found for: {username}')

                                                usernames.remove(username)
                                                print(f'{username} removed from complete username list')

                                                with open("complete_username_list.txt", "w") as f:
                                                    for item in usernames:
                                                        f.write(item + "\n")
                                                print('complete_username_list.txt updated')

                                                # CLOSE MEDIA POP UP WINDOW
                                                try:
                                                    print('Closing media pop-up window')
                                                    close_media = wait.until(
                                                        ec.presence_of_element_located(
                                                            (By.XPATH, '/html/body/div[2]/div/div/'
                                                                       'div/div[2]/div/div/div[1]/'
                                                                       'div/div[2]/div/div')))

                                                    time.sleep(3)
                                                    close_media.click()
                                                    continue
                                                except NoSuchElementException:
                                                    print('NOT able to close Media Pop-up Window')
                                                    break

                                        except NoSuchElementException:
                                            print(f'Heart button NOT found for: {username}')

                                            usernames.remove(username)
                                            print(f'{username} removed from complete username list')

                                            with open("complete_username_list.txt", "w") as f:
                                                for item in usernames:
                                                    f.write(item + "\n")
                                            print('complete_username_list.txt updated')

                                            # CLOSE MEDIA POP UP WINDOW
                                            try:
                                                print('Closing media pop-up window')
                                                close_media = wait.until(
                                                    ec.presence_of_element_located(
                                                        (By.XPATH, '/html/body/div[2]/div/div/'
                                                                   'div/div[2]/div/div/div[1]/'
                                                                   'div/div[2]/div/div')))

                                                time.sleep(3)
                                                close_media.click()
                                                continue
                                            except NoSuchElementException:
                                                print('NOT able to close Media Pop-up Window')
                                                break

                                    except NoSuchElementException:
                                        print(f'Next button NOT found for: {username}')

                                        usernames.remove(username)
                                        print(f'{username} removed from complete username list')

                                        with open("complete_username_list.txt", "w") as f:
                                            for item in usernames:
                                                f.write(item + "\n")
                                        print('complete_username_list.txt updated')

                                        # CLOSE MEDIA POP UP WINDOW
                                        try:
                                            print('Closing media pop-up window')
                                            close_media = wait.until(
                                                ec.presence_of_element_located(
                                                    (By.XPATH, '/html/body/div[2]/div/div/'
                                                               'div/div[2]/div/div/div[1]/'
                                                               'div/div[2]/div/div')))

                                            time.sleep(3)
                                            close_media.click()
                                            continue
                                        except NoSuchElementException:
                                            print('NOT able to close Media Pop-up Window')
                                            break

                                except NoSuchElementException:
                                    print(f'Heart button NOT found for: {username}')

                                    usernames.remove(username)
                                    print(f'{username} removed from complete username list')

                                    with open("complete_username_list.txt", "w") as f:
                                        for item in usernames:
                                            f.write(item + "\n")
                                    print('complete_username_list.txt updated')

                                    # CLOSE MEDIA POP UP WINDOW
                                    try:
                                        print('Closing media pop-up window')
                                        close_media = wait.until(
                                            ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/'
                                                                                      'div/div[2]/div/div/div[1]/'
                                                                                      'div/div[2]/div/div')))

                                        time.sleep(3)
                                        close_media.click()
                                        continue
                                    except NoSuchElementException:
                                        print('NOT able to close Media Pop-up Window')
                                        break

                            except NoSuchElementException:
                                print(f'Next Button NOT found for: {username}')

                                usernames.remove(username)
                                print(f'{username} removed from complete username list')

                                with open("complete_username_list.txt", "w") as f:
                                    for item in usernames:
                                        f.write(item + "\n")
                                print('complete_username_list.txt updated')

                                # CLOSE MEDIA POP UP WINDOW
                                try:
                                    print('Closing media pop-up window')
                                    close_media = wait.until(
                                        ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/'
                                                                                  'div/div[2]/div/div/div[1]/'
                                                                                  'div/div[2]/div/div')))

                                    time.sleep(3)
                                    close_media.click()
                                    continue
                                except NoSuchElementException:
                                    print('NOT able to close Media Pop-up Window')
                                    break

                        except NoSuchElementException:
                            print(f'Heart Button NOT found for: {username}')

                            usernames.remove(username)
                            print(f'{username} removed from complete username list')

                            with open("complete_username_list.txt", "w") as f:
                                for item in usernames:
                                    f.write(item + "\n")
                            print('complete_username_list.txt updated')

                            # CLOSE MEDIA POP UP WINDOW
                            try:
                                print('Closing media pop-up window')
                                close_media = wait.until(
                                    ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/'
                                                                              'div/div[2]/div/div/div[1]/'
                                                                              'div/div[2]/div/div')))

                                time.sleep(3)
                                close_media.click()
                                continue
                            except NoSuchElementException:
                                print('NOT able to close Media Pop-up Window')
                                break

                    except NoSuchElementException:
                        print(f'Next Button NOT found for: {username}')

                        usernames.remove(username)
                        print(f'{username} removed from complete username list')

                        with open("complete_username_list.txt", "w") as f:
                            for item in usernames:
                                f.write(item + "\n")
                        print('complete_username_list.txt updated')

                        # CLOSE MEDIA POP UP WINDOW
                        try:
                            print('Closing media pop-up window')
                            close_media = wait.until(
                                ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/'
                                                                          'div/div[2]/div/div/div[1]/'
                                                                          'div/div[2]/div/div')))

                            time.sleep(3)
                            close_media.click()
                            continue
                        except NoSuchElementException:
                            print('NOT able to close Media Pop-up Window')
                            break

                except NoSuchElementException:
                    print(f'Heart Button NOT found for: {username}')

                    usernames.remove(username)
                    print(f'{username} removed from complete username list')

                    with open("complete_username_list.txt", "w") as f:
                        for item in usernames:
                            f.write(item + "\n")
                    print('complete_username_list.txt updated')
                    # CLOSE MEDIA POP UP WINDOW
                    try:
                        print('Closing media pop-up window')
                        close_media = wait.until(
                            ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/'
                                                                      'div/div[2]/div/div/div[1]/'
                                                                      'div/div[2]/div/div')))

                        time.sleep(3)
                        close_media.click()
                        continue
                    except NoSuchElementException:
                        print('NOT able to close Media Pop-up Window')
                        break

            except NoSuchElementException:
                print(f'No Posts found for: {username}')

                usernames.remove(username)
                print(f'{username} removed from complete username list')

                with open("complete_username_list.txt", "w") as f:
                    for item in usernames:
                        f.write(item + "\n")
                print('complete_username_list.txt updated')
                continue

        except NoSuchElementException:
            print(f'{username} not found')

            usernames.remove(username)
            print(f'{username} removed from complete username list')

            with open("complete_username_list.txt", "w") as f:
                for item in usernames:
                    f.write(item + "\n")
            print('complete_username_list.txt updated')
            continue
        except TimeoutException:
            print(f'{username} not found')

            usernames.remove(username)
            print(f'{username} removed from complete username list')

            with open("complete_username_list.txt", "w") as f:
                for item in usernames:
                    f.write(item + "\n")
            print('complete_username_list.txt updated')
            continue

