# -*- coding: spec -*-
# This is a comparison of DSL syntax to what is generated

import nose
import nose.tools
from sure import expect, this

import json
from noseOfYeti.tokeniser.support import noy_sup_setUp
from unittest import TestCase
import nose

import python_jsonschema_objects as pjs

describe TestCase, 'validators':

  context 'additionalItems':

    before_each:
      self.schema = {
          'title': 'Test Schema',
          "definitions": {
            "numeric": {
              "type": "number"
              }
            },
          "properties": {
            "reffed": {
              "type": "object",
              "additionalProperties": {"$ref": "#/definitions/numeric"}
              },
            "direct": {
              "type": "object",
              "additionalProperties": {"type": "number"}
              },
            "disallowed": {
              "type": "object",
              "properties": {
                "allowed": {"type": "string"},
                },
              "additionalProperties": False
              }
            }
          }

      builder = pjs.ObjectBuilder(self.schema)
      builder.should.be.ok
      self.ns = builder.build_classes()


    it 'should disallow additionalProperties when false':

      self.ns.TestSchema.when.called_with(
          **{
            'disallowed': {
              'allowed': 'me', 'notallowed': 'me'
              }
            }
          ).should.throw(pjs.ValidationError)

    it 'should enforce referenced additionalProperties types':

        self.ns.TestSchema.when.called_with(
            **{
              'reffed': {
                'allowed': 'me'
                }
              }
            ).should.throw(pjs.ValidationError)

        self.ns.TestSchema.when.called_with(
            **{
              'reffed': {
                'allowed': 12345
                }
              }
            ).should_not.throw(pjs.ValidationError)

        testObject = self.ns.TestSchema(**{
              'reffed': {
                'allowed': 12345
                }
              }
            )

        int(testObject.reffed.allowed).should.equal(12345)

    it 'should enforce direct additionalProperties types':

        self.ns.TestSchema.when.called_with(
            **{
              'direct': {
                'allowed': 'me'
                }
              }
            ).should.throw(pjs.ValidationError)

        self.ns.TestSchema.when.called_with(
            **{
              'direct': {
                'allowed': 12345
                }
              }
            ).should_not.throw(pjs.ValidationError)

        testObject = self.ns.TestSchema(**{
              'direct': {
                'allowed': 12345
                }
              }
            )

        int(testObject.direct.allowed).should.equal(12345)
