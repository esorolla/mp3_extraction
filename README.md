# mp3_extraction
This program extracts the mp3 files from the website *"albalearning.com"* corresponding to the stored audiobooks within (mainly in Spanish).

The script uses the module **BeautifulSoup** from the **bs4** package to download the mp3 files corresponding to the audiobooks whose authors list is provided within the main() function. The user has the possibility to create the authors list manually by entering the keywords defining them according to the website design or by extracting initially the keywords of **ALL** the authors stored on the website and later filtering according to his criterion.

The script works correctly except for some books/authors where the webpage may present some defect. For instance, the book entitled *"El elixir de larga vida"* stored on the website *"https://albalearning.com/audiolibros/balzac/elixir.html"* repeats the link for the first part of the audiobook as for the second part, leading to a problem that can be easily identified and solved manually. Nevertheless, the algorithm used relies on some sort of tag building pattern so that particular mistakes like this one cannot be predicted and solved automatically because they deviate from the norm. In this case this occurs as a simple misprint commited by the web developer of the site.

The script can be easily adapted for extraction of other files from different sites with similar html tag structure. Nevertheless, for the moment the program has just been used on the above-mentioned website with excellent performance.