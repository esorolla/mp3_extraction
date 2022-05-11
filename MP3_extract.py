################################################################################
#                                                                              #
# This program downloads automatically the mp3 files stored on the website     #
# "albalearning.com". The idea is to input the URL of the root webpage and     #
# the script retrieves the links found within. Later the script visits the     #
# corresponding sites and automatically downloads the mp3 files.               #
#                                                                              #
################################################################################
import requests
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm


def get_chapters_links(input_url, root_link):
    """
    This function extracts the links of the chapters of the book extracted.
    To do so we keep just the links whose address includes the name of the
    corresponding book.
    --------------------------------------------------------------------------
    Input:
        input_url --> (str) storing the link of the book found.
        root_link --> (str) storing the root of the webpage.
    Output:
        links --> (set)(str) storing all the links of the chapters of the book.
    """
    internal_links = get_links(input_url)[0]
    # Keeps links whose address includes the name of the requested author
    links = [link for link in internal_links if root_link in link]
    return links


def get_mp3_links(mp3_url):
    """
    This function extracts the links where the mp3 files are stored.
    -----------------------------------------------------------------
    Input:
        mp3_url --> (str) storing the link of a webpage possibly hosting an
                          mp3 file.
    Output:
        links --> (str) storing all the mp3 links.
    """
    try:
        website_content = requests.get(mp3_url.strip()).text
    except AssertionError as error:
        print(error)
        check_internet = requests.get('https://google.com').status_code

        if check_internet != requests.codes.ok:
            raise ConnectionError('ERROR: Check internet connection.')
    else:
        _soup = BeautifulSoup(website_content, features='html.parser')

        def with_string(src):  # function to define
            return src and re.compile('.*.mp3').search(src)

        links = []
        for link in _soup.find_all('source', src=with_string):
            links.append(link['src'])
        return links
    finally:
        pass


def download_mp3_files(url, links, file_path, parent_dir):
    """
    This function downloads all the mp3 files stored on the retrieved links.
    -------------------------------------------------------------------------
    Input:
        url --> (str) storing the address of the author's webpage.
        links --> (list)(str) storing the local links addressing the
                              mp3 files on the author's webpage.
        file_path --> (str) defining the path of the folder on your PC where
                            the books of the current author are downloaded.
        parent_dir --> (str) defining the path of the root folder on your PC.
    Output:
        None
    """
    author_root = url[:url.rfind('/')+1]
    print(f'\nauthor_root: {author_root}')
    full_links = [author_root + link for link in links]
    for link in tqdm(full_links, position=1, desc='link', leave=False,
                     colour='red', ncols=80):
        mp3_link = get_mp3_links(link)  # retrieves all the links where mp3 files are stored

        if len(mp3_link) == 0:  # no mp3 link found on this webpage
            root_link = link[link.rfind('/')+1:-5]  # local link of the book
            new_file_path = file_path + '\\' + root_link
            os.makedirs(new_file_path, exist_ok=True)
            new_links = get_chapters_links(link, root_link)  # new internal links
            new_full_links = [author_root + link for link in new_links]

            for new_link in new_full_links:
                new_mp3_link = get_mp3_links(new_link)

                if len(new_mp3_link) == 0:
                    print(f'new_mp3_link: {new_mp3_link}')
                    logfile = parent_dir+'\log.txt'
                    now = datetime.now() # current date and time
                    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
                    with open(logfile, 'a+', encoding='utf-8') as f:
                        f.write('Logged time: ')
                        f.write(date_time)
                        f.write('\nWARNING: The new_link: "')
                        f.write(new_link)
                        f.write('"\n')
                        f.write('Very likely the website of this link has')
                        f.write(' several chapters or a link is wrong!\n\n')
                    continue

                mp3_link = new_mp3_link[0]
                doc = requests.get(mp3_link)
                filename = mp3_link[mp3_link.rfind('/')+1:]
                # Next line must be modified if using another root webpage
                new_filename = filename[filename.find('/albalearning-')+14:]
                with open(new_file_path+'\\'+new_filename, 'wb') as f:
                    f.write(doc.content)
        elif len(mp3_link) > 1:
            logfile = parent_dir+'\log.txt'
            now = datetime.now() # current date and time
            date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
            with open(logfile, 'a+', encoding='utf-8') as f:
                f.write('Logged time: ')
                f.write(date_time)
                f.write('WARNING: More than one mp3 file have been found on: "')
                f.write(link)
                f.write('"\n')
                f.write('Very likely the website of this link has several')
                f.write(' versions.')
        else:
            mp3_link = mp3_link[0]
            doc = requests.get(mp3_link)
            filename = mp3_link[mp3_link.rfind('/')+1:]
            new_filename = filename[filename.rfind('-')+1:]  # renames file
            with open(file_path+'\\'+new_filename, 'wb') as f:
                f.write(doc.content)
    return None


def filter_links(links):
    """
    This function filters the links extracted with the function "get_links"
    so that we just keep the ones directing to webpages where books of the
    requested author are stored. We need to apply this step because on the
    authors webpages there also exist other external and internal webpages
    corresponding to sections unconnected to the author's books.
    --------------------------------------------------------------------------
    Input:
        links --> (set)(str) storing the set of all internal links.
    Output:
        clean_links --> (set)(str) storing the set of all internal links
                                   corresponding to addresses with stored
                                   books from the corresponding author.
    """

    # Removes links with '#', '/', '-en.' or '-fr.' so that we avoid links
    # different from authors' books or books in English or French.
    regex = re.compile(r'([#/]|(-en.)|(-fr.))')
    clean_links = [link for link in links if not regex.search(link)]
    return clean_links


def get_links(url):
    """
    This function extracts the links from the root webpage.
    --------------------------------------------------------
    Input:
        url --> (str) storing the root webpage address.
    Output:
        internal_links --> (set)(str) storing all the internal links on the
                                      root webpage.
        external_links --> (set)(str) storing all the external links.
    """
    if not url or len(url) < 1:
        raise Exception('INFO: Invalid Input')
    try:
        website_content = requests.get(url.strip()).text
    except AssertionError as error:
        print(error)
        check_internet = requests.get('https://google.com').status_code

        if check_internet != requests.codes.ok:
            raise ConnectionError('ERROR: Check internet connection.')
    else:
        if len(website_content) == 0:
            raise Exception('INFO: Website was not retrieved!')
        _soup = BeautifulSoup(website_content, features='html.parser')

        internal_links = set()
        external_links = set()

        # We search for the links:
        for line in _soup.find_all('a'):
            link = line.get('href')
            if not link:
                continue
            if link.startswith('http'):
                external_links.add(link)
            else:
                internal_links.add(link)

        return [internal_links, external_links]
    finally:
        pass


def set_variables(web_root, author_keywords):
    """
    This function sets the parent directory, and the list of URLs hosting
    the websites with the books from the author list, joining the web_root
    to the author keywords.
    ---------------------------------------------------------------------
    Input:
        webroot --> (str) storing the web address of the web root.
        author_keywords --> (str) storing the list of keywords defining the
                                  authors on the website.
    Output:
        parent_dir --> (str) absolute path where this script is located.
        user_input_urls --> (list)(str) list with the web addresses of the
                                        requested authors.
    """
    abspath = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abspath)
    os.chdir(parent_dir)
    user_input_urls = [web_root + elem + '/' for elem in author_keywords]

    return parent_dir, user_input_urls


def get_author_keywords(web_root):
    """
    This function obtains the keywords corresponding to the authors of the
    books stored on the webpage whose address is stored in the root webpage.
    ------------------------------------------------------------------------
    Input:
        web_root --> (str) storing the address of the root webpage.
    Output:
        author_list --> (list)(str) storing the list of keywords representing
                                    the authors of books on the root webpage.
    """
    if not web_root or len(web_root) < 1:
        raise Exception('INFO: Invalid Input')
    try:
        website_content = requests.get(web_root.strip()).text
    except AssertionError as error:
        print(error)
        check_internet = requests.get('https://google.com').status_code

        if check_internet != requests.codes.ok:
            raise ConnectionError('ERROR: Check internet connection.')
    else:
        if len(website_content) == 0:
            raise Exception('INFO: Website was not retrieved!')
        _soup = BeautifulSoup(website_content, features='html.parser')

        author_list = []

        # We search for the author keywords list:
        for line in _soup.find_all('td', class_='lista-libros1'):
            for element in line.find_all('a'):
                author_key = element.get('href')
                if not author_key:
                    continue
                else:
                    author_list.append(author_key)

        return author_list
    finally:
        pass


def main():
    """
    This function downloads automatically the mp3 files from the requested
    authors stored on the root webpage. The user must enter the list of
    keywords corresponding to the requested authors and the script downloads
    automatically the audiobooks.
    ---------------------------------------------------------------------------
    Input:
        None
    Output:
        None
    Action:
        Download the mp3 files automatically.
    """
    web_root = 'https://albalearning.com/audiolibros/'
    author_keywords = ['benedetti', 'benavente', 'hesse']  # author list manually defined
    #author_keywords = get_author_keywords(web_root)
    print(f'authors list: {author_keywords}')
    parent_dir, user_input_urls = set_variables(web_root, author_keywords)
    for url in tqdm(user_input_urls, position=0, desc='url', leave=True,
                    colour='green', ncols=80):
        links = get_links(url)[0]
        links = filter_links(links)
        folder = author_keywords[user_input_urls.index(url)]
        file_path = os.path.join(parent_dir, folder)
        os.makedirs(file_path, exist_ok=True)
        download_mp3_files(url, links, file_path, parent_dir)
    return None


if __name__ == '__main__':
    main()
