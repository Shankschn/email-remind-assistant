from django.contrib.auth.models import User


def create_user(account, email, password, first_name, last_name, is_staff):
    is_success = False
    try:
        user = User.objects.create_user(account, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = 1
        user.is_staff = is_staff
        user.save()
    except Exception as e:
        print(e)
    else:
        is_success = True
    return is_success


def import_users(txt):
    is_success = False
    fgf1 = '##'
    fgf2 = '——'
    users = txt.split(fgf1)
    for user in users:
        if user != '':
            temp = user.split(fgf2)
            is_success = create_user(temp[0], temp[1], temp[2], temp[3], temp[4], temp[5])
    return is_success
