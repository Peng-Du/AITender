import time
import os
import argparse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# 读取账户信息
def get_credentials(file_path='Account.txt'):
    with open(file_path, 'r') as f:
        username = f.readline().strip()
        password = f.readline().strip()
    return username, password

def main(target_date_str):
    # 获取账户信息
    username, password = get_credentials()

    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 创建下载目录
    download_dir_name = f"Download{target_date_str}"
    download_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'TenderBase', download_dir_name))
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # 设置下载路径
    prefs = {"download.default_directory": download_dir}
    options.add_experimental_option("prefs", prefs)

    # 初始化WebDriver
    # 脚本在 ChromeDriverManager().install() 处挂起，通常是由于环境限制（例如 PowerShell）。
    # 解决方法是手动下载 chromedriver。
    # 1. 检查您的 Chrome 版本（设置 -> 关于Chrome）。
    # 2. 从 https://googlechromelabs.github.io/chrome-for-testing/ 下载匹配的 chromedriver。
    # 3. 将 chromedriver.exe 放置在此脚本所在的目录中。
    service = Service(executable_path='..//..//AI//Chromedriver//chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    # 增强反爬虫检测规避
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            });
        """
    })

    try:
        # 1. 直接访问登录页面
        driver.get('https://www.adjudicacionestic.com/front/login.php')

        # 等待并根据更新后的选择器填充用户名和密码（登录超时设置为5分钟）
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='eMail']"))).send_keys(username)
        driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
        
        # 尝试多种方式定位登录按钮
        try:
            # 方式1: 通过按钮文本
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Acceder')]")
        except NoSuchElementException:
            try:
                # 方式2: 通过input类型为submit
                login_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            except NoSuchElementException:
                # 方式3: 通过class或其他属性
                login_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@value='Acceder'] | //*[contains(@class, 'btn') and contains(text(), 'Acceder')]")
        
        login_button.click()

        try:
            # 等待登录成功后跳转到licitaciones页面
            time.sleep(3)  # 等待登录完成
            print("登录成功，正在跳转到licitaciones页面...")
            
            # 跳转到指定页面
            driver.get('https://www.adjudicacionestic.com/front/licitaciones.php')
            print("已成功跳转到licitaciones页面")
            
            # 等待页面完全加载
            time.sleep(3)
            
            # 尝试下拉页面以确保所有元素加载
            print("正在下拉页面以加载所有内容...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 根据HTML结构，使用更精确的ID和类型来定位'Buscar'搜索框
            print("正在查找'Buscar'搜索框...")
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='licitaciones_filter']//input[@type='search']"))
            )
            print("找到Buscar搜索框")

            # 2. 在Buscar搜索框中输入'hardware'并搜索
            search_box.clear()  # 清空搜索框
            search_box.send_keys('hardware')
            print("已在搜索框中输入hardware")
            
            # 提交搜索或按回车键
            from selenium.webdriver.common.keys import Keys
            search_box.send_keys(Keys.RETURN)
            print("正在搜索hardware相关项目...")
            
            # 等待搜索结果加载
            time.sleep(5)
            
            # 查看搜索结果列表
            try:
                print("正在查看搜索结果列表...")
                # 查找搜索结果表格或列表
                results_table = driver.find_elements(By.XPATH, "//table//tr | //div[contains(@class, 'result')] | //ul//li")
                if results_table:
                    print(f"找到 {len(results_table)} 个搜索结果项")
                    # 显示前几个结果的信息
                    for i, result in enumerate(results_table[:5]):
                        try:
                            result_text = result.text.strip()
                            if result_text and len(result_text) > 10:  # 过滤掉空白或太短的结果
                                print(f"结果 {i+1}: {result_text[:100]}...")  # 显示前100个字符
                        except:
                            continue
                else:
                    print("未找到搜索结果列表")
            except Exception as list_error:
                print(f"查看搜索结果列表时出错: {list_error}")
            
            # 下载当前项目列表
            try:
                print("正在下载项目列表...")
                
                # 查找CSV下载按钮
                csv_button = driver.find_element(By.XPATH, "//a[contains(text(), 'CSV') or contains(@class, 'csv')]")
                if csv_button:
                    csv_button.click()
                    print("CSV文件下载中...")
                    time.sleep(5)
                
                # 也可以下载Excel格式
                try:
                    excel_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Excel') or contains(@class, 'excel')]")
                    if excel_button:
                        excel_button.click()
                        print("Excel文件下载中...")
                        time.sleep(5)
                except:
                    print("Excel下载按钮未找到或已下载CSV")
                    
            except Exception as download_error:
                print(f"下载项目列表时出错: {download_error}")

            # 创建一个集合来存储已下载的项目ID，以避免重复下载
            downloaded_ids = set()

            # 循环处理所有页面
            page_count = 1
            while True:
                try:
                    print(f"\n--- 开始处理第 {page_count} 页 --- ")
                    print("开始处理当前页面的项目...")
                    # 获取当前页面所有包含'hardware'的结果行
                    project_rows = driver.find_elements(By.XPATH, "//table[@id='licitaciones']/tbody/tr[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'hardware')]")
                    print(f"在当前页面找到 {len(project_rows)} 个包含'hardware'的项目。")

                    if not project_rows:
                        print("当前页面没有找到'hardware'项目。")
                    else:
                        stop_processing = False
                        for row in project_rows:
                            try:
                                # 从行的id属性（例如 'licita-159203'）中提取数字ID
                                row_id_attr = row.get_attribute('id')
                                # 新增：提取并检查日期
                                try:
                                    date_str = row.find_element(By.XPATH, "./td[contains(@class, 'sorting_1')]").text
                                    project_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()

                                    print(f"项目日期: {project_date}, 目标日期: {target_date}")

                                    if project_date != target_date:
                                        print(f"项目日期 {project_date} 不是目标日期 {target_date}，跳过。")
                                        if project_date < target_date:
                                            print("项目日期早于目标日期，停止处理后续页面。")
                                            stop_processing = True
                                            break
                                        continue
                                except Exception as date_exc:
                                    print(f"无法解析日期: {date_exc}")
                                    continue # 继续处理下一行

                                if row_id_attr and 'licita-' in row_id_attr:
                                    project_id = row_id_attr.split('-')[-1]

                                    # 检查此ID是否已下载
                                    if project_id in downloaded_ids:
                                        print(f"项目 {project_id} 已下载，跳过。")
                                        continue

                                    print(f"\n提取到新项目ID: {project_id}")

                                    # 构建直接下载链接
                                    download_url = f"https://www.adjudicacionestic.com/front/descarga-adjudicacion.php?tipo=PPT&id={project_id}"
                                    print(f"准备从URL下载: {download_url}")

                                    # 在新标签页中打开下载链接以下载文件
                                    driver.execute_script(f"window.open('{download_url}', '_blank');")
                                    print(f"ID {project_id} 的文件下载中...")
                                    time.sleep(10)  # 等待下载开始

                                    # 将成功下载的ID添加到集合中
                                    downloaded_ids.add(project_id)
                                    print(f"项目 {project_id} 已成功添加到下载记录中。")
                                else:
                                    print(f"警告: 无法从行中提取ID: {row.text[:80]}...")
                            except Exception as download_exc:
                                print(f"处理单个项目时出错: {download_exc}")
                        
                        if stop_processing:
                            break # 跳出 while 循环

                    # 尝试点击“Siguiente”（下一页）按钮
                    try:
                        # 找到并点击“下一页”按钮
                        print("\n正在查找 'Siguiente' 按钮...")
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, 'licitaciones_next'))
                        )
                        print("找到'Siguiente'按钮，使用JavaScript点击...")
                        driver.execute_script("arguments[0].click();", next_button)

                        # 使用强制等待代替复杂的等待逻辑
                        print("已点击'Siguiente'按钮，强制等待5秒以加载新页面...")
                        time.sleep(5)
                        print("等待结束，准备处理新页面。")
                        page_count += 1

                    except (NoSuchElementException, TimeoutException):
                        print("\n未找到可点击的'Siguiente'按钮，已到达最后一页。")
                        break  # 退出循环

                except Exception as page_error:
                    print(f"处理页面时发生错误: {page_error}")
                    break

        except TimeoutException:
            print("登录超时或失败。浏览器当前页面URL为:", driver.current_url)
            print("请检查浏览器窗口，查看是否出现错误信息、CAPTCHA或预期之外的页面。")
            # 尝试查找常见的错误信息元素
            try:
                # 这是一个通用的错误信息选择器，您可能需要根据实际页面进行调整
                error_element = driver.find_element(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert')]")
                print(f"检测到错误信息: {error_element.text}")
            except NoSuchElementException:
                print("未找到明确的错误信息。请检查您的账户凭据是否正确，或网站结构是否已更改。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭浏览器
        driver.quit()  # 确保浏览器在脚本执行完毕后关闭
        print("脚本执行完毕")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download tender documents for a specific date.')
    parser.add_argument('--date', help='The target date in YYYY-MM-DD format. Defaults to today.', default=datetime.now().strftime('%Y-%m-%d'))
    args = parser.parse_args()
    main(args.date)