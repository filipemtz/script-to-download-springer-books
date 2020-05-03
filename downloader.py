
import os
import urllib.request, urllib.error, urllib.parse


def read_data(fname):
    with open(fname, "r", encoding="utf8") as f:
        lines = f.readlines()

    data = []

    for l in lines:
        l = l.rstrip().rsplit(",")
        if len(l[0]) > 0:
            data.append({
                "title": l[0],
                "year": l[4],
                "url": l[-4],
                "subject": l[-3].rsplit(";")[0]
            })

    return data


def download_document(url):
    # download page with the link the download the pdf
    response = urllib.request.urlopen(url)
    webContent = str(response.read())
    # search for the link to the pdf
    link = [l for l in webContent.split("\\n") if "Download this book in PDF format" in l]
    if len(link) < 1:
        print("Download link not found for URL=", url)
        return None
    # format the link to download the pdf
    link = link[0].strip().lstrip("<a href=\"")
    link = link[:link.find("\"")]
    link = "https://link.springer.com" + link
    # download the pdf
    r = urllib.request.urlopen(link)
    return r.read()


def create_dir_if_necessary(dir):
    if not os.path.isdir(dir):
        print("Creating dir:", dir)
        os.mkdir(dir)


def save_pdf(path, doc):
    with open(path, 'wb') as g: 
        g.write(doc)
        print("Saved:", path)


def save_failures(fname, failures):
    with open(fname, "w") as h:
        failures = [",".join(d) for d in failures]
        h.write("\n".join(failures))


if __name__ == "__main__":
    input_file = "books.csv"
    output_dir = "books"
    fail_file = "failures.csv"

    data = read_data(input_file)
    data = data[1:]  # discard header
    failures = [] 
    
    create_dir_if_necessary(output_dir)

    for d in data:
        dir = output_dir + "/" + d["subject"] 
        create_dir_if_necessary(dir)

        # remove spaces and other non-alphanumeric characters
        title = "".join([c for c in d["title"] if c.isalnum()])
        pdf_path = "%s/%s_%s.pdf" % (dir, d["year"], title)
        
        if not os.path.exists(pdf_path):
            doc = download_document(d["url"])
            if doc is not None:
                save_pdf(pdf_path, doc)
            else:
                failures.append(d)
        else:
            print("Skipping book already saved:", pdf_path)
    
    save_failures("failures.csv", failures)


