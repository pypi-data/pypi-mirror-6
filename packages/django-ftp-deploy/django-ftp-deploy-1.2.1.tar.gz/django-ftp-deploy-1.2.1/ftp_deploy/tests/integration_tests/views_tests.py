import time

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ftp_deploy.tests.utils.factories import AdminUserFactory, ServiceFactory, LogFactory, NotificationFactory
from ftp_deploy.models import Service


class ViewsTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(5)
        self.wait = WebDriverWait(self.browser, 5)

    def tearDown(self):
        self.browser.quit()

    def user_authenticate(self):
        AdminUserFactory()
        self.browser.get(self.live_server_url + reverse('ftpdeploy_login'))
        self.wait.until(lambda browser: browser.find_element_by_tag_name('form'))
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)
        self.wait_for_load()
        time.sleep(1)

    def wait_for_load(self):
        return self.wait.until(lambda browser: browser.find_element_by_tag_name('header'))

    def test_top_navigation(self):
        self.user_authenticate()

        # User click 'Service' link and see 'Services Dashboard' header
        navbar = self.browser.find_element_by_class_name('navbar')
        navbar.find_element_by_link_text('Services').click()
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Services Dashboard', page_header)

        # User click 'Notification' link and see 'Notificaions Dashboard' header
        navbar = self.browser.find_element_by_class_name('navbar')
        navbar.find_element_by_link_text('Notifications').click()
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Notifications Dashboard', page_header)

        # User click 'Add Service' link and see service form
        navbar = self.browser.find_element_by_class_name('navbar')
        navbar.find_element_by_link_text('Add').click()
        navbar.find_element_by_link_text('Add Service').click()
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Service Add', page_header)

        # User click 'Add Notification' link and see notification form
        navbar = self.browser.find_element_by_class_name('navbar')
        navbar.find_element_by_link_text('Add').click()
        navbar.find_element_by_link_text('Add Notification').click()
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Notification Add', page_header)

    def test_can_see_login_screen_and_log_in(self):
        # User installed ftp deploy app and visit app login screen in order to log in
        # He notice Login text on page as well
        self.browser.get(self.live_server_url + reverse('ftpdeploy_login'))
        self.wait.until(lambda browser: browser.find_element_by_tag_name('form'))
        body = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Login', body)

        # He type data into username and password but make a typo,
        # that couse comes up error message box

        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin1')
        password_field.send_keys(Keys.RETURN)
        self.wait.until(lambda browser: browser.find_element_by_class_name('alert-danger'), 'Error message after fail login attempt')

        # At third attempt he make it! type proper username and password, login
        # and redirect to dashboard page
        AdminUserFactory()
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('admin')
        password_field.send_keys(Keys.RETURN)
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Services Dashboard', page_header)

        # When he try visit login page after success login, he is redirect to dashboard page again
        self.browser.get(self.live_server_url + reverse('ftpdeploy_login'))
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Services Dashboard', page_header)

    def test_can_log_out(self):
        self.user_authenticate()

        # User click logout link and redirect to login screen
        self.browser.find_element_by_xpath("//a[@href='%s']" % reverse('ftpdeploy_logout')).click()
        self.wait.until(lambda browser: browser.find_element_by_tag_name('form'))

        # After visit login screen again he stay on the login page
        self.browser.get(self.live_server_url + reverse('ftpdeploy_login'))
        self.wait.until(lambda browser: browser.find_element_by_tag_name('form'))

        body = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Login', body)

        self.browser.save_screenshot('screen.png')

    def test_can_see_notification_page_and_manage_notifications(self):
        self.user_authenticate()

        # self.browser.save_screenshot('screen.png')

        # User go to notification page by click Notification link on left hand side menu
        page = self.browser.find_element_by_id('page')
        page.find_element_by_link_text("Notifications").click()
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text

        # He can see Notification Dashboard title
        self.assertIn('Notifications Dashboard', page_header)

        # He is welcome with message and see big 'Add Notification' button
        page = self.browser.find_element_by_id('page')
        page.find_element_by_class_name('well')

        add_notification_btn = self.browser.find_element_by_class_name('btn-success')
        self.assertIn('Add Notification', add_notification_btn.text)

        # He click Add notification button and see form with option to add new email, and two others DEPLOY USER and COMMIT USER
        add_notification_btn.click()
        self.wait_for_load()
        self.assertIn('Notification Add', self.browser.find_element_by_class_name('page-header').text)

        form = self.browser.find_element_by_tag_name('form')
        self.assertIn('DEPLOY USER', form.text)
        self.assertIn('COMMIT USER', form.text)

        # He name notification entry - Default.
        name_field = form.find_element_by_name('name')
        name_field.send_keys('Default')

        # He add email but accidently input invalid emial and input error state. Next he add three correct emails
        email_input = form.find_element_by_id('email')
        add_email_btn = form.find_element_by_link_text('Add Email')

        email_input.send_keys('email1.emai.com')
        add_email_btn.click()
        self.wait_for_load()

        email_input.clear()
        email_input.send_keys('email1@emal.com')
        add_email_btn.click()
        email_input.send_keys('email2@emal.com')
        add_email_btn.click()
        email_input.send_keys('email3@emal.com')
        add_email_btn.click()

        # He can see all emails on the list
        self.assertIn('email1@emal.com', form.text)
        self.assertIn('email2@emal.com', form.text)
        self.assertIn('email3@emal.com', form.text)

        # He decided he doesn't need last email and click remove button next to the third email,
        # and noticed email is not on the list any more
        last_email_row = self.browser.find_element_by_xpath("//form/table/tbody/tr[3]")
        last_email_row.find_element_by_class_name('remove').click()
        self.assertNotIn('email3@emal.com', form.text)

        # He untick SUCCESS and first email
        first_email_row = self.browser.find_element_by_xpath("//form/table/tbody/tr[1]")
        first_email_row.find_element_by_name("_success").click()

        # He untick SUCCESS and FAIL for second email
        second_email_row = self.browser.find_element_by_xpath("//form/table/tbody/tr[2]")
        second_email_row.find_element_by_name("_success").click()
        second_email_row.find_element_by_name("_fail").click()

        # He tick DEPLOY USER - SUCCESS, and COMMIT USER - FAIL and save
        form.find_element_by_id('id_deploy_user_1').click()
        form.find_element_by_id('id_commit_user_2').click()
        form.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for_load()

        # He noticed success message after success submit
        self.browser.find_element_by_class_name('alert-success')

        # He can see Default notification title on the list
        table = self.browser.find_element_by_class_name('table')
        self.assertIn('Default', table.text)

        # He click edit notification button to confirm all is ok, and noticed second email hadn't been saved. He can see only first email
        # and he realize he unticked SUCCESS and FAIL for secont email.
        first_notification_row = self.browser.find_element_by_xpath("//table/tbody/tr[1]")
        first_notification_row.find_element_by_link_text('Edit').click()

        form = self.browser.find_element_by_tag_name('form')
        self.assertIn('email1@emal.com', form.text)
        self.assertNotIn('email2@emal.com', form.text)

        # He confirm all settings looks correct and save
        first_email_row = self.browser.find_element_by_xpath("//form/table/tbody/tr[1]")
        self.assertFalse(first_email_row.find_element_by_name('_success').is_selected())
        self.assertTrue(first_email_row.find_element_by_name('_fail').is_selected())

        self.assertTrue(form.find_element_by_id('id_deploy_user_1').is_selected())
        self.assertFalse(form.find_element_by_id('id_deploy_user_2').is_selected())
        self.assertTrue(form.find_element_by_id('id_commit_user_2').is_selected())
        self.assertFalse(form.find_element_by_id('id_commit_user_1').is_selected())
        form.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for_load()

        # He can see another Add Notification button on the page
        # He add new notification witout any information and name it No Notifications
        page = self.browser.find_element_by_id('page')
        page.find_element_by_link_text('Add Notification').click()
        self.assertIn('Notification Add', self.browser.find_element_by_tag_name('body').text)

        form = self.browser.find_element_by_tag_name('form')
        name_field = form.find_element_by_name('name')
        name_field.send_keys('No Notifications')
        form.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for_load()

        # He notice he has two entries on Notification list then.
        table = self.browser.find_element_by_class_name('table')
        self.assertIn('Default', table.text)
        self.assertIn('No Notifications', table.text)
        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 2)

        # He realize he doesn't need second notification for now, so delete it
        # and notice delete confitmation message
        second_email_row = self.browser.find_element_by_xpath("//table/tbody/tr[2]")
        second_email_row.find_element_by_class_name('dropdown-toggle').click()
        second_email_row.find_element_by_link_text('Delete').click()
        second_email_row.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for_load()
        self.browser.find_element_by_class_name('alert-success')

        # He can see only one notification on the list again.
        table = self.browser.find_element_by_class_name('table')
        self.assertIn('Default', table.text)
        self.assertNotIn('No Notifications', table.text)
        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 1)
        # self.browser.save_screenshot('screen.png')

    def test_can_see_and_use_log_page(self):
        self.user_authenticate()

        # User go to log page by click Log link on top menu
        nav = self.browser.find_element_by_xpath("//div[@role='navigation']")
        nav.find_element_by_link_text("Log").click()
        self.wait_for_load()

        # He noticed Log Dashboard header
        # along with empty log table
        page_header = self.browser.find_element_by_class_name('page-header').text
        self.assertIn('Log', page_header)
        table_first_row = self.browser.find_element_by_xpath("//table/tbody/tr[1]")
        self.assertIn('No Results', table_first_row.text)

        # He create 2 services and perform one deploy each.
        service1 = ServiceFactory()
        service2 = ServiceFactory()
        Log1 = LogFactory(service=service1)
        Log2 = LogFactory(service=service1, status=False)
        Log3 = LogFactory(service=service2)

        self.browser.get(self.live_server_url + reverse('ftpdeploy_log'))
        self.wait_for_load()

        # He noticed there are log entries in table
        # In addition he notices one deploy fail
        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 3)

        # He test log filter
        # he tick fail status and see only one row in table

        form = self.browser.find_element_by_id('log-filter')
        form.find_element_by_id('status').click()
        time.sleep(0.1)

        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 1)

        table_first_row = self.browser.find_element_by_xpath("//table/tbody/tr[1]")
        self.assertIn(Log2.service.repo_name, table_first_row.text)

        # after he untick fail only checkbox and is able to see all 3 rows again

        form.find_element_by_id('status').click()
        time.sleep(0.1)
        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 3)

        # next he select log with first service1 assign to it,
        # and see two rows in table with appropriate service repo name

        form.find_element_by_tag_name('select')
        options = form.find_elements_by_tag_name('option')

        for option in options:
            if option.text == Log1.service.repo_name:
                option.click()

        time.sleep(0.1)
        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 2)

        table = self.browser.find_element_by_tag_name('table')
        self.assertIn(Log1.service.repo_name, table.text)

        # afterwords he select log with service2 assign to it
        # and see only one row in table with appropriate service repo name

        form.find_element_by_tag_name('select')
        options = form.find_elements_by_tag_name('option')

        for option in options:
            if option.text == Log3.service.repo_name:
                option.click()

        time.sleep(0.1)
        table_rows = self.browser.find_elements_by_xpath("//table/tbody/tr")
        self.assertEqual(len(table_rows), 1)

        table = self.browser.find_element_by_tag_name('table')
        self.assertIn(Log3.service.repo_name, table.text)

        self.browser.save_screenshot('screen.png')

    def test_can_see_service_dashboard_page_and_manage_services(self):

        self.user_authenticate()

        # User go to services page by click left menu 'Services' link

        page = self.browser.find_element_by_id('page')
        page.find_element_by_link_text("Services").click()
        self.wait_for_load()
        page_header = self.browser.find_element_by_class_name('page-header').text

        # He can see Services Dashboard title
        self.assertIn('Services Dashboard', page_header)

        # He is welcome with message and see big 'Add Service' button
        page = self.browser.find_element_by_id('page')
        page.find_element_by_class_name('well')
        add_service_btn = self.browser.find_element_by_class_name('btn-success')
        self.assertIn('Add Service', add_service_btn.text)

        # He click Add service button and go do service form page
        add_service_btn.click()
        self.wait_for_load()
        self.assertIn('Service Add', self.browser.find_element_by_class_name('page-header').text)

        page = self.browser.find_element_by_id('page')
        page.find_element_by_id('service-form')

        # Saveing checking is omit intentionaly because of cost of validation process
        # Service is add programmatically without check process

        service1 = ServiceFactory(repo_hook=False, status=False)
        service2 = ServiceFactory(repo_hook=False, status=False)
        service3 = ServiceFactory(repo_hook=False, status=False)

        self.browser.get(self.live_server_url + reverse('ftpdeploy_dashboard'))
        self.wait_for_load()

        # After he added 3 services, he can see all of them on the list
        service_list = self.browser.find_element_by_id('service-list')
        self.assertIn(service1.repo_name, service_list.text)
        self.assertIn(service2.repo_name, service_list.text)
        self.assertIn(service3.repo_name, service_list.text)

        # He use filter and confirm filter works as expected

        form = self.browser.find_element_by_id('service-filter')
        options = form.find_elements_by_tag_name('option')

        for option in options:
            if option.text == service1.repo_name:
                option.click()

        time.sleep(0.1)
        table_rows = self.browser.find_elements_by_xpath("//tbody[@id='service-list']/tr")
        self.assertEqual(len(table_rows), 1)

        table = self.browser.find_element_by_id('service-list')
        self.assertIn(service1.repo_name, table.text)
        self.assertNotIn(service2.repo_name, table.text)
        self.assertNotIn(service3.repo_name, table.text)

        for option in options:
            if option.text == service2.repo_name:
                option.click()

        time.sleep(0.1)
        table_rows = self.browser.find_elements_by_xpath("//tbody[@id='service-list']/tr")
        self.assertEqual(len(table_rows), 1)

        table = self.browser.find_element_by_id('service-list')
        self.assertIn(service2.repo_name, table.text)
        self.assertNotIn(service1.repo_name, table.text)
        self.assertNotIn(service3.repo_name, table.text)

        # He noticed he can add new service by the 'Add Service' if service already exist as well
        # He click it and see add service form again.

        page = self.browser.find_element_by_id('page')
        page.find_element_by_link_text('Add Service').click()
        self.wait_for_load()

        page = self.browser.find_element_by_id('page')
        page.find_element_by_id('service-form')
        self.browser.get(self.live_server_url + reverse('ftpdeploy_dashboard'))
        self.wait_for_load()

        # He click 'Edit' link next to the service and go to edit form. He noticed thah form is prepopulated by saved values

        first_service = self.browser.find_element_by_xpath("//tbody[@id='service-list']/tr[1]")
        first_service.find_element_by_link_text('Edit').click()
        self.wait_for_load()

        form = self.browser.find_element_by_id('service-form')
        repo_name = self.browser.find_element_by_id('id_repo_name')
        secret_key = self.browser.find_element_by_id('id_secret_key')

        self.assertIn(service1.repo_name, repo_name.get_attribute('value'))
        self.assertIn(service1.secret_key, secret_key.get_attribute('value'))

        # He notice there is 'Manage' link on page header. He click it and go to Manage Page

        page_header = self.browser.find_element_by_class_name('page-header')
        page_header.find_element_by_link_text('Manage').click()
        self.wait_for_load()

        page_header = self.browser.find_element_by_class_name('page-header')
        self.assertIn('%s Manage' % service1.repo_name, page_header.text)

        self.browser.get(self.live_server_url + reverse('ftpdeploy_dashboard'))
        self.wait_for_load()

        # He click 'Manage' link next to the service and go to manage page

        first_service = self.browser.find_element_by_xpath("//tbody[@id='service-list']/tr[1]")
        first_service.find_element_by_link_text('Manage').click()
        self.wait_for_load()

        # He can see 'Repo_name Manage' header
        page_header = self.browser.find_element_by_class_name('page-header')
        self.assertIn('%s Manage' % service1.repo_name, page_header.text)

        # He notice service status fail because of invalid hook, and see 'Add hook' link

        page = self.browser.find_element_by_id('page')
        self.assertIn('Add hook', page.text)

        # Add hook link test is omit because of time consuming by request
        # check flag is change programmatically

        service = Service.objects.get(pk=service1.pk)
        service.repo_hook = True
        service.save()

        self.browser.get(self.live_server_url + reverse('ftpdeploy_service_manage', args=(service.pk,)))
        self.wait_for_load()

        # After he click 'Add hook' he noticed that link disappear
        page = self.browser.find_element_by_id('page')
        self.assertNotIn('Add hook', page.text)

        # After few commits he can see Recent deploys table with latests deploys
        log1 = LogFactory(service=service1)
        log2 = LogFactory(service=service1)
        log3 = LogFactory(service=service1, status=False)
        log4 = LogFactory(service=service1, status=False)

        self.browser.get(self.live_server_url + reverse('ftpdeploy_service_manage', args=(service.pk,)))
        self.wait_for_load()

        # He notice two of deploys fails, and is able to see Fail Deploys table along with 'Restore Deploys' button.
        fail_deploys = self.browser.find_element_by_id('fail-deploys')
        fail_deploys.find_element_by_link_text('Restore Deploys')
        restore_list_rows = self.browser.find_elements_by_xpath("//tbody[@id='restore-list']/tr")
        self.assertEqual(len(restore_list_rows), 2)

        # He decided to skip first of failed deploys, and click 'Skip' button,
        # and then skip entry is not in 'Fail Deploys' table any more

        first_fail_deploy_row = self.browser.find_element_by_xpath("//tbody[@id='restore-list']/tr[1]")
        first_fail_deploy_row.find_element_by_link_text('Skip').click()
        first_fail_deploy_row.find_element_by_link_text('Confirm').click()

        self.browser.get(self.live_server_url + reverse('ftpdeploy_service_manage', args=(service.pk,)))
        self.wait_for_load()

        restore_list_rows = self.browser.find_elements_by_xpath("//tbody[@id='restore-list']/tr")
        self.assertEqual(len(restore_list_rows), 1)

        # He cilck 'Restore Deploys' and see popup with 'Restore Tree' title

        fail_deploys = self.browser.find_element_by_id('fail-deploys')
        fail_deploys.find_element_by_link_text('Restore Deploys').click()

        self.wait.until(lambda browser: browser.find_element_by_id('restore-modal'))

        time.sleep(1)
        restore_modal = self.browser.find_element_by_id('restore-modal')
        modal_title = restore_modal.find_element_by_class_name('modal-title')
        self.assertIn('Restore Tree', restore_modal.text)

        # He is able to see 'New', 'Modified' and 'Removed' files in restore information
        # along with commits informations
        self.assertIn('New', restore_modal.text)
        self.assertIn('Modified', restore_modal.text)
        self.assertIn('Removed', restore_modal.text)
        self.assertIn('commit 1', restore_modal.text)
        self.assertIn('commit 2', restore_modal.text)

        # He click close button and close modal window
        restore_modal.find_element_by_xpath("//button[@data-dismiss='modal']").click()
        time.sleep(1)
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Restore Tree', body.text)

        # He decided change notifications for service so he click 'Notification' link
        notification = NotificationFactory(name='Default')

        self.browser.find_element_by_id('notification').click()
        self.wait.until(lambda browser: browser.find_element_by_id('notification-modal'))
        time.sleep(1)
        restore_modal = self.browser.find_element_by_id('notification-modal')
        modal_title = restore_modal.find_element_by_class_name('modal-title')
        self.assertIn('Notification', restore_modal.text)

        # In the popup he select 'Default' notification and click save
        form = self.browser.find_element_by_id('notification-form')
        options = form.find_elements_by_tag_name('option')

        for option in options:
            if option.text == notification.name:
                option.click()

        time.sleep(1)
        form.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for_load()
        # He see save notification success message
        self.browser.find_element_by_class_name('alert-success')

        # He see notification name in Statistics section
        page = self.browser.find_element_by_id('page')
        self.assertIn('Notifications: Default', page.text)

        # He noticed status icon is actually a link to refresh service status
        self.browser.find_element_by_xpath("//a[@id='service-manage-status']")

        # He click 'Edit' link and see service edit form
        page_header = self.browser.find_element_by_class_name('page-header')
        page_header.find_element_by_link_text('Edit').click()
        self.wait_for_load()

        form = self.browser.find_element_by_id('service-form')
        repo_name = self.browser.find_element_by_id('id_repo_name')
        secret_key = self.browser.find_element_by_id('id_secret_key')

        self.assertIn(service1.repo_name, repo_name.get_attribute('value'))
        self.assertIn(service1.secret_key, secret_key.get_attribute('value'))

        # He decide to delete service and click 'Delete' link, and then confirm delete
        page_header = self.browser.find_element_by_class_name('page-header')
        page_header.find_element_by_class_name('dropdown-toggle').click()
        page_header.find_element_by_link_text('Delete').click()
        page_header.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for_load()
        self.browser.find_element_by_class_name('alert-success')

        # He is redirect to service dashboard
        # see success message and doesn't see removed service on the list any more
        self.browser.find_element_by_class_name('alert-success')

        service_list = self.browser.find_element_by_id('service-list')
        self.assertNotIn(service1.repo_name, service_list.text)
        self.assertIn(service2.repo_name, service_list.text)
        self.assertIn(service3.repo_name, service_list.text)

        self.browser.save_screenshot('screen.png')
