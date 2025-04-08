images_attache = {
    "776725864517430" : 'https://synapxe.workvivo.com/document/link/74327'
}

files_attache = {
    '263077399797550' : 'https://synapxe.workvivo.com/document/link/74420'
}

files_attache_swapped = {v: k for k, v in files_attache.items()}


default_image_id = 'https://synapxe.workvivo.com/document/link/74327'
default_file_id = 'https://synapxe.workvivo.com/document/link/74420'


def attachment_mapper(id_, type_):
    if type_ == "image":
        return images_attache.get(id_, default_image_id)
    elif type_ == "file":
        return files_attache.get(id_, default_file_id)
    else:
        return ""
    

def attachment_mapper_swapped(url):
    return files_attache_swapped.get(url, "")
