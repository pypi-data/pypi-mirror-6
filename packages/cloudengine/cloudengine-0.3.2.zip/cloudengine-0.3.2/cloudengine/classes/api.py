
import logging
import json
from rest_framework.response import Response
from rest_framework import status
from cloudengine.classes.manager import ClassesManager
from cloudengine.core.cloudapi_view import CloudAPIView

logger = logging.getLogger("cloudengine")

manager = ClassesManager()


class AppClassesView(CloudAPIView):
    
    def get(self, request):
        app = request.META.get('app',"")
        if not app:
            return Response({'detail': 'App id not provided'}, 
                                    status=401)
        app_classes = manager.get_classes(app.name)
        return Response({"result": app_classes})


class ClassView(CloudAPIView):

    DEFAULT_QUERY = '{}'

    def get(self, request, cls):
        app = request.META.get('app', None)
        if not app:
            return Response({'detail': 'App id not provided'}, status=400)
        # Django automatically urldecodes query string
        query_str = request.GET.get('query', self.DEFAULT_QUERY)
        logger.info("query string received: %s" % query_str)
        try:
            # urlparse the query
            query = json.loads(query_str)
        except Exception:
            return Response({"detail": "Invalid query"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        
        
        try:
            # urlparse the query
            order_str = request.GET['orderby']
            order_obj = json.loads(order_str)
            assert(len(order_obj) == 1)      # sorting possible only on one key
            order_by = order_obj.keys()[0]
            order = order_obj.values()[0]
        except AssertionError:
            return Response({'detail': 'orderby option takes only one property value'},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        except Exception, e:
            order_by = order = None
        try:
            res = manager.get_class(app.name, cls, query, order_by, order)
        except Exception, e:
            return Response({'detail': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            exception=True)
        return Response({"result": res})

    def delete(self, request, cls):
        app = request.META.get('app', None)
        if not app:
            return Response({'detail': 'App id not provided'}, status=400)
        manager.delete_class( app.name, cls)
        return Response()

    def post(self, request, cls):
        app = request.META.get('app', None)
        if not app:
            return Response({'detail': 'App id not provided'}, status=400)
        try:
            logger.debug("request body recieved: %s"%request.body)
            new_obj = json.loads(request.body)
        except Exception, e:
            logger.error("Unable to decode object. Error: %s"%str(e))
            return Response({"detail": "Invalid object."},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        try:
            objid = manager.add_object(app.name, cls, new_obj)
        except Exception as e:
            return Response({
                "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
                            )
        return Response({"_id": str(objid)}, status=201)


class ObjectView(CloudAPIView):

    def get(self, request, cls, objid):
        logger.info("get request from %s for object %s" %
                    (request.user.username, objid))
        app = request.META.get('app', None)
        if not app:
            return Response({'detail': 'App id not provided'}, status=400)
        try:
            obj = manager.get_object(app.name, cls, objid)
        except Exception, e:
            return Response({"detail": "Invalid object id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        if obj:
            return Response({"result": obj})
        else:
            return Response({"detail": "Invalid object id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)

    # todo: put should actually replace the existing objects
    # since updating only a few fields does not affect the existing fields, in
    # case the user wanted to delete a few fields. Android: Object.remove()
    # todo: _id cannot be updated by the request
    def put(self, request, cls, objid):
        app = request.META.get('app', None)
        if not app:
            return Response({'detail': 'App id not provided'}, status=400)
        try:
            obj = json.loads(request.body)
        except Exception:
            return Response({"detail": "Invalid object id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        try:
            manager.update_object(app.name, cls, objid, obj)
        except Exception as e:
                return Response({
                    "detail": "Invalid object. _id/app_id is a reserved field"},
                    status=status.HTTP_400_BAD_REQUEST
                                )
        return Response()

    def delete(self, request, cls, objid):
        app = request.META.get('app', None)
        if not app:
            return Response({'detail': 'App id not provided'}, status=400)
        manager.delete_object(app.name, cls, objid)
        return Response()

