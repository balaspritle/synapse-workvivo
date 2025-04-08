images_attache = {
    "219107941113257": "https://synapxe.workvivo.com/document/link/74327",
    "752700373525299": "https://synapxe.workvivo.com/document/link/74328",
    "242489695524051": "https://synapxe.workvivo.com/document/link/74339",
    "1079779633080561": "https://synapxe.workvivo.com/document/link/74333",
    "373652717783778": "https://synapxe.workvivo.com/document/link/74315",
    "3237924849817570": "https://synapxe.workvivo.com/document/link/74335",
    "1429747661142196": "https://synapxe.workvivo.com/document/link/74332",
    "618421875886190": "https://synapxe.workvivo.com/document/link/74316",
    "295369082510842": "https://synapxe.workvivo.com/document/link/74337",
    "1110845112982902": "https://synapxe.workvivo.com/document/link/74330",
    "1115822986428072": "https://synapxe.workvivo.com/document/link/74336",
    "772625221096183": "https://synapxe.workvivo.com/document/link/74338",
    "772525921478614": "https://synapxe.workvivo.com/document/link/74318",
    "1779936562526367": "https://synapxe.workvivo.com/document/link/74322",
    "392597213703592": "https://synapxe.workvivo.com/document/link/74321",
    "776725864517430": "https://synapxe.workvivo.com/document/link/74331",
    "1166340107439417": "https://synapxe.workvivo.com/document/link/74323",
    "686765138991063": "https://synapxe.workvivo.com/document/link/74326",
    "228999339592196": "https://synapxe.workvivo.com/document/link/74325",
    "676204697883726": "https://synapxe.workvivo.com/document/link/74336",
    "1476543166619071": "https://synapxe.workvivo.com/document/link/74324",
    "659588972757679": "https://synapxe.workvivo.com/document/link/74319",
    "5347295205315367": "https://synapxe.workvivo.com/document/link/74329",
    "1102455810699927": "https://synapxe.workvivo.com/document/link/74320",
    "798326961763465": "https://synapxe.workvivo.com/document/link/74334",
    "297801119440328": "https://synapxe.workvivo.com/document/link/74317"
}

files_attache = {
    "277106861605434": "https://synapxe.workvivo.com/document/link/74423",
    "1206132606917580": "https://synapxe.workvivo.com/document/link/74410",
    "4886989338076491": "https://synapxe.workvivo.com/document/link/74404",
    "3562295917315600": "https://synapxe.workvivo.com/document/link/74405",
    "357243206292199": "https://synapxe.workvivo.com/document/link/74406",
    "606787288233113": "https://synapxe.workvivo.com/document/link/74422",
    "677356030463488": "https://synapxe.workvivo.com/document/link/74412",
    "630218859209162": "https://synapxe.workvivo.com/document/link/74420",
    "423522686466172": "https://synapxe.workvivo.com/document/link/74419",
    "1432235347624488": "https://synapxe.workvivo.com/document/link/74402",
    "255409003945195": "https://synapxe.workvivo.com/document/link/74413",
    "255206000641803": "https://synapxe.workvivo.com/document/link/74415",
    "263077399797550": "https://synapxe.workvivo.com/document/link/74417",
    "813019073665148": "https://synapxe.workvivo.com/document/link/74408",
    "944941766577465": "https://synapxe.workvivo.com/document/link/74403",
    "1922055144831257": "https://synapxe.workvivo.com/document/link/74418"
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
