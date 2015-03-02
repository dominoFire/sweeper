from azure_subscription import sms

result = sms.list_os_images()

result = [x for x in result if x.os.lower()=='linux']

single_result = result[0]

for image in result:
    print('Name: ' + image.name)
    print('Label: ' + image.label)
    print('OS: ' + image.os)
    print('Category: ' + image.category)
    #print('Description: ' + image.description)
    print('Location: ' + image.location)
    #print('Affinity group: ' + image.affinity_group)
    print('Media link: ' + image.media_link)
    print('')
