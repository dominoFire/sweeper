__author__ = 'fer'
"""
NOTE: This file must be replaced when the new version of de Azure SDK for Phyton
will be released
"""
import sys
import time
from azure.servicemanagement import ServiceManagementService


# --Operations for tracking asynchronous requests ---------------------
def wait_for_operation_status_progress_default_callback(elapsed):
    sys.stdout.write('.')


def wait_for_operation_status_success_default_callback(elapsed):
    sys.stdout.write('\n')


def wait_for_operation_status_failure_default_callback(elapsed, ex):
    sys.stdout.write('\n')
    sys.stdout.write(vars(ex.result))
    raise ex


class AzureSMSAsyncHandler(ServiceManagementService):
    def wait_for_operation_status(self,
                                  request_id, wait_for_status='Succeeded', timeout=30, sleep_interval=5,
                                  progress_callback=wait_for_operation_status_progress_default_callback,
                                  success_callback=wait_for_operation_status_success_default_callback,
                                  failure_callback=wait_for_operation_status_failure_default_callback):
        """
        Waits for an asynchronous operation to complete.
        This calls get_operation_status in a loop and returns when the expected
        status is reached. The result of get_operation_status is returned. By
        default, an exception is raised on timeout or error status.

        :param request_id: The request ID for the request you wish to track.
        :param wait_for_status: Status to wait for. Default is 'Succeeded'.
        :param timeout: Total timeout in seconds. Default is 30s.
        :param sleep_interval: Sleep time in seconds for each iteration. Default is 5s.
        :param progress_callback:
            Callback for each iteration.
            Default prints '.'.
            Set it to None for no progress notification.
        :param success_callback:
            Callback on success. Default prints newline.
            Set it to None for no success notification.
        :param failure_callback:
            Callback on failure. Default prints newline+error details then
            raises exception.
            Set it to None for no failure notification.
        :return:
        """
        loops = timeout // sleep_interval + 1
        start_time = time.time()
        for _ in range(loops):
            result = self.get_operation_status(request_id)
            elapsed = time.time() - start_time
            if result.status == wait_for_status:
                if success_callback is not None:
                    success_callback(elapsed)
                return result
            elif result.error:
                if failure_callback is not None:
                    #ex = WindowsAzureAsyncOperationError(_ERROR_ASYNC_OP_FAILURE, result)
                    ex = IOError()
                    failure_callback(elapsed, ex)
                return result
            else:
                if progress_callback is not None:
                    progress_callback(elapsed)
                time.sleep(sleep_interval)

        if failure_callback is not None:
            #ex = WindowsAzureAsyncOperationError(_ERROR_ASYNC_OP_TIMEOUT, result)
            ex = IOError()
            failure_callback(elapsed, ex)
        return result
