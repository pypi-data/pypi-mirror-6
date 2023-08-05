# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Agents
------

Contained within this module are API handling functions which can
    * create new agents
    * update existing agent data
    * delete existing agents
"""

from functools import partial
from httplib import NOT_FOUND, NO_CONTENT, OK, CREATED, BAD_REQUEST
from flask import request
from flask.views import MethodView
from pyfarm.core.logger import getLogger
from pyfarm.core.enums import APIError
from pyfarm.models.agent import Agent
from pyfarm.master.application import db
from pyfarm.master.utility import (
    JSONResponse, json_from_request, get_column_sets)

ALL_AGENT_COLUMNS, REQUIRED_AGENT_COLUMNS = get_column_sets(Agent)

# partial function(s) to assist in data conversion
to_json = partial(json_from_request,
                  all_keys=ALL_AGENT_COLUMNS,
                  required_keys=REQUIRED_AGENT_COLUMNS,
                  disallowed_keys=set(["id"]))

logger = getLogger("api.agents")


def schema():
    """
    Returns the basic schema of :class:`.Agent`

    .. http:get:: /api/v1/agents/schema HTTP/1.1

        **Request**

        .. sourcecode:: http

            GET /api/v1/agents/schema HTTP/1.1
            Accept: application/json

        **Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "ram": "INTEGER",
                "free_ram": "INTEGER",
                "use_address": "INTEGER",
                "ip": "IPv4Address",
                "hostname": "VARCHAR(255)",
                "cpus": "INTEGER",
                "port": "INTEGER",
                "state": "INTEGER",
                "ram_allocation": "FLOAT",
                "cpu_allocation": "FLOAT",
                "id": "INTEGER",
                "remote_ip": "IPv4Address"
            }

    :statuscode 200: no error
    """
    return JSONResponse(Agent().to_schema())


class AgentIndexAPI(MethodView):
    # TODO: should return agent
    def post(self):
        """
        A ``POST`` to this endpoint will do one of two things:

            * update an existing agent and return the row
            * create a new agent and return the row

        In order to update an existing agent the following columns
        must match an existing agent.  Generally speaking however, this
        functionality is included solely limit the number of duplicate
        agents:

            * hostname
            * port
            * ram
            * cpus

        If the incoming request contains data (from the list above) that
        matches an existing agent, the existing agent will be updated and
        returned.  In all other cases, a ``POST`` to this endpoint will
        result in the creation of a new agent.

        .. http:post:: /api/v1/agents HTTP/1.1

            **Request**

            .. sourcecode:: http

                POST /api/v1/agents HTTP/1.1
                Accept: application/json

                {
                    "cpu_allocation": 1.0,
                    "cpus": 14,
                    "free_ram": 133,
                    "hostname": "agent1",
                    "ip": "10.196.200.115",
                    "port": 64994,
                    "ram": 2157,
                    "ram_allocation": 0.8,
                    "state": 8
                 }


            **Response (existing agent updated)**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Content-Type: application/json

                {
                    "cpu_allocation": 1.0,
                    "cpus": 14,
                    "free_ram": 133,
                    "hostname": "agent1",
                    "id": 1,
                    "ip": "10.196.200.115",
                    "port": 64994,
                    "ram": 2157,
                    "ram_allocation": 0.8,
                    "state": 8
                 }

            **Request**

            .. sourcecode:: http

                POST /api/v1/agents HTTP/1.1
                Accept: application/json

                {
                    "cpu_allocation": 1.0,
                    "cpus": 14,
                    "free_ram": 133,
                    "hostname": "agent1",
                    "ip": "10.196.200.115",
                    "port": 64994,
                    "ram": 2157,
                    "ram_allocation": 0.8,
                    "state": 8
                 }

            **Response (agent created)**

            .. sourcecode:: http

                HTTP/1.1 201 CREATED
                Content-Type: application/json

                {
                    "cpu_allocation": 1.0,
                    "cpus": 14,
                    "free_ram": 133,
                    "hostname": "agent1",
                    "id": 1,
                    "ip": "10.196.200.115",
                    "port": 64994,
                    "ram": 2157,
                    "ram_allocation": 0.8,
                    "state": 8
                 }

        :statuscode 200: an existing agent was updated
        :statuscode 201: a new agent was created
        :statuscode 400: there was something wrong with the request (such as
                         invalid columns being included)
        """
        # get json data from the request
        data = to_json(request)
        if isinstance(data, JSONResponse):
            return data

        request_columns = set(data)

        # request did not include at least the required columns
        if (request_columns != REQUIRED_AGENT_COLUMNS
                and request_columns.issubset(REQUIRED_AGENT_COLUMNS)):
            errorno, msg = APIError.MISSING_FIELDS
            msg += ": %s" % list(REQUIRED_AGENT_COLUMNS - request_columns)
            return JSONResponse((errorno, msg), status=BAD_REQUEST)

        # request included some columns which don't exist
        elif not request_columns.issubset(ALL_AGENT_COLUMNS):
            errorno, msg = APIError.EXTRA_FIELDS_ERROR
            extra_columns = list(request_columns - ALL_AGENT_COLUMNS)
            msg = "the following columns do not exist: %s" % extra_columns
            return JSONResponse((errorno, msg), status=BAD_REQUEST)

        # update with our remote_addr from the request
        data.update(remote_ip=request.remote_addr)

        # check to see if there's already an existing agent with
        # this information
        existing_agent = Agent.query.filter_by(
            hostname=data["hostname"], port=data["port"]).first()

        # agent already exists, try to update it
        if existing_agent:
            updated = {}
            for key, value in data.iteritems():
                if getattr(existing_agent, key) != value:
                    setattr(existing_agent, key, value)
                    updated[key] = value

            # if not fields were updated, nothing to do here
            if updated:
                logger.debug(
                    "updated agent %s: %s" % (existing_agent.id, updated))
                db.session.add(existing_agent)
                db.session.commit()

            return JSONResponse(existing_agent.to_dict(), status=OK)

        # didn't find an agent that matched the incoming data
        # so we'll create one
        else:
            new_agent = Agent(**data)
            db.session.add(new_agent)
            db.session.commit()
            agent_data = new_agent.to_dict()
            logger.info("created agent %s: %s" % (new_agent.id, agent_data))
            return JSONResponse(agent_data, status=CREATED)


class SingleAgentAPI(MethodView):
    """
    API view which is used for retrieving information about and updating
    single agents.
    """
    def get(self, agent_id=None):
        """
        Return basic information about a single agent

        .. http:get:: /api/v1/agents/(int:agent_id) HTTP/1.1

            **Request (agent exists)**

            .. sourcecode:: http

                GET /api/v1/agents/1 HTTP/1.1
                Accept: application/json

            **Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Content-Type: application/json

                {
                    "cpu_allocation": 1.0,
                    "cpus": 14,
                    "free_ram": 133,
                    "hostname": "agent1",
                    "id": 1,
                    "ip": "10.196.200.115",
                    "port": 64994,
                    "ram": 2157,
                    "ram_allocation": 0.8,
                    "state": 8
                 }

            **Request (no such agent)**

            .. sourcecode:: http

                GET /api/v1/agents/1234 HTTP/1.1
                Accept: application/json

            **Response**

            .. sourcecode:: http

                HTTP/1.1 404 NOT FOUND
                Content-Type: application/json

                [4, "no agent found for `1234`"]

        :statuscode 200: no error
        :statuscode 404: no agent could be found using the given id
        """
        agent = Agent.query.filter_by(id=agent_id).first()
        if agent is not None:
            return JSONResponse(agent.to_dict())
        else:
            errorno, msg = APIError.DATABASE_ERROR
            msg = "no agent found for `%s`" % agent_id
            return JSONResponse((errorno, msg), status=NOT_FOUND)

    # TODO: docs need a few more examples here
    def post(self, agent_id=None):
        """
        Update an agent's columns with new information

        .. http:post:: /api/v1/agents/(int:agent_id) HTTP/1.1

            **Request**

            .. sourcecode:: http

                POST /api/v1/agents/1 HTTP/1.1
                Accept: application/json

                {"ram": 1234}


            **Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Content-Type: application/json

                {
                    "cpu_allocation": 1.0,
                    "cpus": 14,
                    "free_ram": 133,
                    "hostname": "agent1",
                    "id": 1,
                    "ip": "10.196.200.115",
                    "port": 64994,
                    "ram": 1234,
                    "ram_allocation": 0.8,
                    "state": 8
                }

        :statuscode 200: no error
        :statuscode 400: something within the request is invalid
        :statuscode 404: no agent could be found using the given id
        """
        # get json data
        data = to_json(request)
        if isinstance(data, JSONResponse):
            return data

        # get model
        model = Agent.query.filter_by(id=agent_id).first()
        if model is None:
            errorno, msg = APIError.DATABASE_ERROR
            msg = "no agent found for `%s`" % agent_id
            return JSONResponse((errorno, msg), status=NOT_FOUND)

        # update model
        modified = False
        for key, value in data.iteritems():
            if value != getattr(model, key):
                setattr(model, key, value)
                modified = True

        if modified:
            db.session.add(model)
            db.session.commit()

        return JSONResponse(model.to_dict(), status=OK)

    def delete(self, agent_id=None):
        """
        Delete a single agent

        .. http:delete:: /api/v1/agents/(int:agent_id) HTTP/1.1

            **Request (agent exists)**

            .. sourcecode:: http

                DELETE /api/v1/1 HTTP/1.1
                Accept: application/json

            **Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Content-Type: application/json


            **Request (agent does not exist)**

            .. sourcecode:: http

                DELETE /api/v1/agents/1 HTTP/1.1
                Accept: application/json

            **Response**

            .. sourcecode:: http

                HTTP/1.1 204 NO CONTENT
                Content-Type: application/json

        :statuscode 200: the agent existed and was deleted
        :statuscode 204: the agent did not exist, nothing to delete
        """
        agent = Agent.query.filter_by(id=agent_id).first()
        if agent is None:
            return JSONResponse(status=NO_CONTENT)
        else:
            db.session.delete(agent)
            db.session.commit()
            return JSONResponse(status=OK)
