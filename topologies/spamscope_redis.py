#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2017 Fedele Mantuano (https://twitter.com/fedelemantuano)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from spouts import FilesMailSpout
from bolts import (Attachments, JsonMaker, Phishing, Tokenizer,
                   Urls, Network, RawMail, OutputRedis)
from streamparse import Grouping, Topology


class OutputRedisTopology(Topology):

    files_spout = FilesMailSpout.spec(
        name="files-mails")

    tokenizer = Tokenizer.spec(
        name="tokenizer",
        inputs=[files_spout],
        par=1)

    attachments = Attachments.spec(
        name="attachments",
        inputs={tokenizer['attachments']: Grouping.fields('sha256_random')},
        par=2)

    urls = Urls.spec(
        name="urls",
        inputs={
            attachments: Grouping.fields('sha256_random'),
            tokenizer['body']: Grouping.fields('sha256_random')})

    phishing = Phishing.spec(
        name="phishing",
        inputs={
            attachments: Grouping.fields('sha256_random'),
            tokenizer['mail']: Grouping.fields('sha256_random'),
            urls: Grouping.fields('sha256_random')})

    network = Network.spec(
        name="network",
        inputs={tokenizer['network']: Grouping.fields('sha256_random')},
        par=2)

    raw_mail = RawMail.spec(
        name="raw_mail",
        inputs={tokenizer['raw_mail']: Grouping.fields('sha256_random')},
        par=4)

    json_maker = JsonMaker.spec(
        name="json_maker",
        inputs={
            attachments: Grouping.fields('sha256_random'),
            network: Grouping.fields('sha256_random'),
            phishing: Grouping.fields('sha256_random'),
            raw_mail: Grouping.fields('sha256_random'),
            tokenizer['mail']: Grouping.fields('sha256_random'),
            urls: Grouping.fields('sha256_random')})

    output_redis = OutputRedis.spec(
        name="output-redis",
        inputs=[json_maker])
