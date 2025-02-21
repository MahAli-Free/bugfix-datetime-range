from collections.abc import Callable
from typing import Any

import elasticapm
import grpc

from archipy.configs.base_config import BaseConfig
from archipy.helpers.interceptors.grpc.base.base_grpc_server_interceptor import BaseGrpcServerInterceptor
from archipy.helpers.utils.base_utils import BaseUtils


class GrpcServerTraceInterceptor(BaseGrpcServerInterceptor):
    """A gRPC server interceptor for tracing requests using Elastic APM.

    This interceptor captures and traces gRPC server requests, enabling distributed tracing
    across services. It integrates with Elastic APM to monitor and log transactions.
    """

    def intercept(self, method: Callable, request: Any, context: grpc.ServicerContext):
        """Intercepts a gRPC server call to trace the request using Elastic APM.

        Args:
            method (Callable): The gRPC method being intercepted.
            request (Any): The request object passed to the method.
            context (grpc.ServicerContext): The context of the gRPC call.

        Returns:
            Any: The result of the intercepted gRPC method.

        Raises:
            Exception: If an exception occurs during the method execution, it is captured and logged.

        Notes:
            - If Elastic APM is disabled, the interceptor does nothing and passes the call through.
            - If a trace parent header is present in the metadata, it is used to link the transaction
              to the distributed trace.
            - If no trace parent header is present, a new transaction is started.
        """
        try:
            # Skip tracing if Elastic APM is disabled
            if not BaseConfig.global_config().ELASTIC_APM.ENABLED:
                return method(request, context)

            # Extract method name details from the context
            method_name_model = context.method_name_model

            # Get the Elastic APM client
            client = elasticapm.get_client()

            # Convert metadata to a dictionary for easier access
            metadata_dict = dict(context.invocation_metadata())

            # Check if a trace parent header is present in the metadata
            if parent := elasticapm.trace_parent_from_headers(metadata_dict):
                # Start a transaction linked to the distributed trace
                client.begin_transaction(transaction_type="request", trace_parent=parent)
                try:
                    # Execute the gRPC method
                    result = method(request, context)

                    # End the transaction with a success status
                    client.end_transaction(name=method_name_model.full_name, result="success")
                    return result
                except Exception as e:
                    # End the transaction with a failure status if an exception occurs
                    client.end_transaction(name=method_name_model.full_name, result="failure")
                    raise e
            else:
                # Start a new transaction if no trace parent header is present
                client.begin_transaction(transaction_type="request")
                try:
                    # Execute the gRPC method
                    result = method(request, context)

                    # End the transaction with a success status
                    client.end_transaction(name=method_name_model.full_name, result="success")
                    return result
                except Exception as e:
                    # End the transaction with a failure status if an exception occurs
                    client.end_transaction(name=method_name_model.full_name, result="failure")
                    raise e

        except Exception as exception:
            BaseUtils.capture_exception(exception)
