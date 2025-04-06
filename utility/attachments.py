images_attache = {
    "776725864517430" : 'https://ddei5-0-ctp.trendmicro.com:443/wis/clicktime/v1/query?url=https%3a%2f%2fsynapxe.workvivo.com%2fdocument%2flink%2f74316&umid=8B6B93F3-31DE-E006-A137-9378B3218BC4&auth=146d7ac271cb81a53802810e8fcad10467d2d32a-72ce41d5720673c012173b6626835339ff32111d'
}

files_attache = {
    '263077399797550' : 'https://ddei5-0-ctp.trendmicro.com:443/wis/clicktime/v1/query?url=https%3a%2f%2fsynapxe.workvivo.com%2fdocument%2flink%2f74416&umid=8B6B93F3-31DE-E006-A137-9378B3218BC4&auth=146d7ac271cb81a53802810e8fcad10467d2d32a-36ad61ed93be0790ee782f52ab1974658780831a'
}

files_attache_swapped = {v: k for k, v in files_attache.items()}


default_file_id = 'https://ddei5-0-ctp.trendmicro.com:443/wis/clicktime/v1/query?url=https%3a%2f%2fsynapxe.workvivo.com%2fdocument%2flink%2f74416&umid=8B6B93F3-31DE-E006-A137-9378B3218BC4&auth=146d7ac271cb81a53802810e8fcad10467d2d32a-36ad61ed93be0790ee782f52ab1974658780831a'
default_image_id = 'https://ddei5-0-ctp.trendmicro.com:443/wis/clicktime/v1/query?url=https%3a%2f%2fsynapxe.workvivo.com%2fdocument%2flink%2f74316&umid=8B6B93F3-31DE-E006-A137-9378B3218BC4&auth=146d7ac271cb81a53802810e8fcad10467d2d32a-72ce41d5720673c012173b6626835339ff32111d'


def attachment_mapper(id_, type_):
    if type_ == "image":
        return images_attache.get(id_, default_image_id)
    elif type_ == "file":
        return files_attache.get(id_, default_file_id)
    else:
        return None
    

def attachment_mapper_swapped(url):
    return files_attache_swapped.get(url)
