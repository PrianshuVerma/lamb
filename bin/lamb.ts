#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { LambStack } from '../lib/lamb-stack';

const app = new cdk.App();
new LambStack(app, 'LambStack');
