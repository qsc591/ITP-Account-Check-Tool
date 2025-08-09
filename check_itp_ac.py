import asyncio,os,csv,threading,httpx,time,random
import json
from datetime import datetime
import pytz
import traceback


csv_lock =threading.Lock()
accout_list = []
def Nime():
    tz = pytz.timezone('Asia/Shanghai')
    cn = datetime.now(tz).strftime("%Y-%m-%d-%H:%M:%S")
    return cn

if os.path.exists('isp.txt'):
    if os.path.getsize('isp.txt') != 0:
        pass
    else:
        print(f"{Nime()} Pls Add Proxy for isp.txt")
        time.sleep(11111)
else:
    with open('isp.txt','a',encoding='utf-8') as add_proxy:
        add_proxy.write('放入代理后使用')
        add_proxy.close()
    print(f"{Nime()} isp.txt load Done Pls Add Proxy.....")
    time.sleep(11111)
if os.path.exists('itp_check_account.csv'):
    if os.path.getsize('itp_check_account.csv') != 0:
        with open("itp_check_account.csv", 'r', newline='') as load_acc:
            reader = csv.reader(load_acc)
            next(reader, None)
            acc_data = list(reader)
        accout_list = acc_data
        if len(accout_list) == 0:
            print(f"{Nime()} First Start Pls Add ITP ACC FOR itp_check_account.csv")
            time.sleep(11111)
        print(f"{Nime()} Load ALL ACCOUT Success Total: [ {len(accout_list)} ]")

else:
    with open("itp_check_account.csv", 'a', newline='') as csv_load:
        header = ['Accout_name', 'Accout_password']
        if os.path.getsize('itp_check_account.csv') == 0:
            writer = csv.DictWriter(csv_load, fieldnames=header)
            writer.writeheader()
            csv_load.close()
        print(f"{Nime()} itp_check_account csv add Success")
        print(f"{Nime()} First Start Pls Add ITP ACC FOR itp_check_account.csv")
        time.sleep(11111)

log_file = 'itp_check_log.csv'
if os.path.exists('itp_check_log.csv'):
    pass
else:
    with open("itp_check_log.csv", 'a', newline='') as csv_load:
        header = ["Time",'Accout_name', 'Accout_password','Full Name',"ExpDate","ApprovedTime","AccountState","FaceState"]
        if os.path.getsize('itp_check_log.csv') == 0:
            writer = csv.DictWriter(csv_load, fieldnames=header)
            writer.writeheader()
            csv_load.close()
        print(f"{Nime()} itp_check_account csv add Success")

capmonster = input(f"{Nime()} Setup CapmosnterKey:\n")

threading_num = int(input(f"{Nime()} Setup Tasks Threading:\n"))


def proxy():
    proxy = random.choice(open('isp.txt').readlines())
    proxy = proxy.replace('\n', '').split(':')
    httpproxy = {
        "http": f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}',
        "https": f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'
    }
    return httpproxy
async def capmonster_cf(name,api,session:httpx.AsyncClient):
    for tryTasks in range(5):
        try:

            clouflare_body = {
                "clientKey": api,
                "task": {
                    "type": "TurnstileTaskProxyless",
                    "websiteURL": "https://triple.global/en/auth-web/login/email",
                    "websiteKey": '0x4AAAAAABGU_tHsh_LkPT_k',
                }
            }

            rsp = await session.post(url='https://api.capmonster.cloud/createTask', json=clouflare_body)
            taskId = json.loads(rsp.text)['taskId']

            rsp_post = {
                'clientKey': api,
                "taskId": taskId
            }

            while True:
                try:
                    rsp = await session.post('https://api.capmonster.cloud/getTaskResult', json=rsp_post)
                    rsp_data = json.loads(rsp.text)
                    if 'ERROR_CAPTCHA_UNSOLVABLE' in str(rsp.text):
                        break


                    if rsp_data['status'] == 'processing':
                        await asyncio.sleep(1)
                        continue
                    elif rsp_data['status'] == 'ready':
                        return rsp_data['solution']['token']
                    else:
                        print(Nime(),name, "CaptchaError:", rsp_data)
                        break
                except Exception as e:
                    continue
            continue
        except Exception as e:
            if 'Max retries exceeded with' in str(e):
                continue
            print(f"{Nime()} cap get Error{e} {traceback.print_exc()}")
            await asyncio.sleep(1)
        continue

async def itp_login(name,session:httpx.AsyncClient,ac,pas):
    while True:
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh-Hans;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://triple.global',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x18003932) NetType/WIFI Language/zh_CN',
                'x-client-version': 'Chrome/JsCore/11.6.0/FirebaseCore-web',
            }

            params = {
                'key': 'AIzaSyDi1DsEgLRDaWDI2aF7WerqKLqcD5HC8V4',
            }

            json_data = {
                'returnSecureToken': True,
                'email': ac,
                'password': pas,
                'clientType': 'CLIENT_TYPE_WEB',
            }

            login_response = await session.post(
                'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword',
                params=params,
                headers=headers,
                json=json_data
            )


            print(f"{Nime()} {name} {ac} Login State:{login_response.status_code}")
            if login_response.status_code == 200:
                id_token = json.loads(login_response.text)['idToken']
                # print(Nime(),name,id_token)

                headers = {
                    'accept': '*/*',
                    'accept-language': 'zh-CN,zh-Hans;q=0.9',
                    'content-type': 'application/json',
                    'origin': 'https://triple.global',
                    'priority': 'u=1, i',
                    'referer': 'https://triple.global/en/auth-web/login/email',
                    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x18003932) NetType/WIFI Language/zh_CN',
                    'x-service-origin': 'global',
                    'cookie': f'x-triple-web-device-id=ef36aa59-aa89-4bba-a13b-2b94ea6ad6f6-{time.time()*1000}; tk-language=en; _gid=GA1.2.1480653419.1747455988; _fbp=fb.1.1747455988528.955924698835551660; _ga_SQBPDCGR8P=GS2.1.s1747455988$o1$g1$t1747456045$j0$l0$h0; _ga=GA1.2.1766532520.1747455988; _gcl_au=1.1.1007945393.1747455988.724795854.1747455995.1747456051;kint5-web-device-id=f3d40964-ef68-4905-947d-1c7f98f22042',
                }


                json_data = {
                    'fbToken': id_token,
                    'turnstileToken': await capmonster_cf(name=name,api=capmonster,session=session),
                }

                response = await session.post('https://triple.global/auth-web/api/users/auth/login/web', headers=headers,
                                         json=json_data,timeout=5555)

                if response.status_code == 201:
                    try:

                        headers = {
                            'accept': '*/*',
                            'accept-language': 'zh-CN,zh-Hans;q=0.9',
                            'priority': 'u=1, i',
                            'referer': 'https://triple.global/zh-CN/my-info/settings',
                            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"',
                            'sec-fetch-dest': 'empty',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-site': 'same-origin',
                            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x18003932) NetType/WIFI Language/zh_CN',
                            'x-service-origin': 'global',
                        }

                        response = await session.get('https://triple.global/api/users/enter', headers=headers)
                        ekyc_json_data = json.loads(response.text)
                        if ekyc_json_data['enterHasEkyc']:
                            if 'approved' == str(ekyc_json_data['enterEkyc']['status']):
                                #header = ["Time",'Accout_name', 'Accout_password','Full Name',"ExpDate","ApprovedTime","State"]

                                print(f"{Nime()} {name} {ac} {ekyc_json_data['enterEkyc']['userName']} Has Been approved")

                                headers = {
                                    'accept': '*/*',
                                    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                                    'priority': 'u=1, i',
                                    'referer': 'https://triple.global/zh-CN/my-info/facepass/detail',
                                    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                                    'sec-ch-ua-mobile': '?0',
                                    'sec-ch-ua-platform': '"Windows"',
                                    'sec-fetch-dest': 'empty',
                                    'sec-fetch-mode': 'cors',
                                    'sec-fetch-site': 'same-origin',
                                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                                    'x-service-origin': 'global',
                                    'x-triple-user-lang': 'zh-CN',
                                }

                                face_data = await session.get('https://triple.global/api/users/enter/face', headers=headers)
                                face_txt = json.loads(face_data.text)
                                if '无相关人脸识别功能的信息' in str(face_txt):
                                    face = '干净人脸'
                                else:
                                    face = '绑定过人脸'

                                with csv_lock:
                                    with open(log_file, "a", newline='', encoding='utf-8') as file_save:
                                        info_data = {
                                            "Time": Nime(),
                                            "Accout_name": ac,
                                            "Accout_password": pas,
                                            "Full Name": ekyc_json_data['enterEkyc']['userName'],
                                            'ExpDate': ekyc_json_data['enterEkyc']['docExpiredAt'],
                                            "ApprovedTime": ekyc_json_data['enterEkyc']['lastApprovedAt'],
                                            "AccountState": "Verify Done",
                                            "FaceState":face
                                        }
                                        writer = csv.DictWriter(file_save, fieldnames=info_data.keys())
                                        writer.writerow(info_data)
                                        file_save.close()
                                        return True
                            else:
                                with csv_lock:
                                    with open(log_file, "a", newline='',encoding='utf-8') as file_save:
                                        info_data = {"Time": Nime(), "Accout_name": ac,
                                                     "Accout_password": pas,
                                                     "Full Name": ekyc_json_data['enterEkyc']['userName'],
                                                     'ExpDate': ekyc_json_data['enterEkyc']['docExpiredAt'],
                                                     "ApprovedTime": ekyc_json_data['enterEkyc']['lastApprovedAt'],
                                                     "AccountState": "Account Not Verify",
                                                     "FaceState":"None"
                                                     }
                                        writer = csv.DictWriter(file_save,
                                                                fieldnames=info_data.keys())
                                        writer.writerow(info_data)
                                        file_save.close()
                                        return True

                        else:
                            print(f"{Nime()} {name} No Post Data For Kyc:{response.status_code} {response.text}")
                            with open(log_file, "a", newline='', encoding='utf-8') as file_save:
                                info_data = {"Time": Nime(), "Accout_name": ac,
                                             "Accout_password": pas,
                                             "Full Name": None,
                                             'ExpDate': None,
                                             "ApprovedTime": None,
                                             "AccountState": "No KYC DATA",
                                             "FaceState": "None"
                                             }
                                writer = csv.DictWriter(file_save,
                                                        fieldnames=info_data.keys())
                                writer.writerow(info_data)
                                file_save.close()
                                return True
                    except Exception as e:
                        print(Nime(),name,ac,f"Check Accout INFO Error {e} {traceback.print_exc()}")
                        return True
                else:
                    if 'Your account has restricted login access. For further assistance' in str(response.text):
                        print(f"{Nime()} {name} This Accout Has Been Ban [ {ac}:{pas} ]")
                        with csv_lock:
                            file_path = log_file
                            with open(file_path, "a", newline='',encoding='utf-8') as file_save:
                                info_data = {"Time": Nime(), "Accout_name": ac,
                                             "Accout_password": pas,
                                             "Full Name": None,
                                             'ExpDate': None,
                                             "ApprovedTime": None,
                                             "AccountState": "Your account has restricted login access",
                                             "FaceState": None
                                             }
                                writer = csv.DictWriter(file_save,
                                                        fieldnames=info_data.keys())
                                writer.writerow(info_data)
                                file_save.close()
                                return True

                        break

            else:
                print(f"{Nime()} Sent Login Data Error:{login_response.status_code} {login_response.text}")
                if 'INVALID_PASSWORD' in login_response.text:
                    with csv_lock:
                        with open(log_file, "a", newline='', encoding='utf-8') as file_save:
                            info_data = {
                                "Time": Nime(),
                                "Accout_name": ac,
                                "Accout_password": pas,
                                "Full Name": None,
                                'ExpDate': None,
                                "ApprovedTime": None,
                                "AccountState": "Password Error",
                                "FaceState": None
                            }
                            writer = csv.DictWriter(file_save, fieldnames=info_data.keys())
                            writer.writerow(info_data)
                            file_save.close()
                            return True
                continue
        except:
            return False

async def main(td_name):
    global accout_list,threading_num

    while True:
        http_proxy = proxy()
        with csv_lock:
            if not accout_list:
                print(f"{Nime()} {td_name} No More ACC Quit ")
                threading_num -=1
                break

            ac_data = accout_list.pop(0)
            ac = ac_data[0]
            pas = ac_data[1]
            with open(log_file, 'r', encoding='utf-8') as file_check:
                check_same_acc = [line.strip() for line in file_check.readlines()]
                if str(ac) in str(check_same_acc):
                    continue

        print(f"{Nime()} {td_name} Get Data:{ac_data}")

        async with httpx.AsyncClient(proxy=http_proxy['https'], timeout=25, verify=False) as session:
            if await itp_login(name=td_name,session=session,ac=ac,pas=pas):
                continue

            else:
                continue

async def run_tasks_all(tasks_num:int):

    tasks = []
    for kk in range(tasks_num):
        tasks.append(asyncio.create_task(main(f"[Tasks{kk+1}]",)))
    await  asyncio.gather(*tasks)


asyncio.run(run_tasks_all(tasks_num=threading_num))
