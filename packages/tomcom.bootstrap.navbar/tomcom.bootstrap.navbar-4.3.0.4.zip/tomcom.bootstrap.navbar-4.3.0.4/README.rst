Information
===========

A small template to create a bootstrap designed navbar form a category in portal_actions

> <tal:block tal:define="categiries python:['document_actions ']">
>   <metal:block metal:use-macro="context/tcb_navbar/macros/main"/>
> </tal:block>