import { Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';
import * as path from 'path';
import { CfnOutput } from "aws-cdk-lib";
import { FunctionUrlAuthType } from "aws-cdk-lib/aws-lambda";


export class LambStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const seleniumLambda = new DockerImageFunction(this, "SeleniumContainerHandler", {
      code: DockerImageCode.fromImageAsset(path.join(__dirname, '..')),
      memorySize: 2048,
      timeout: Duration.minutes(3),
    });

    const funcUrl = seleniumLambda.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE,  
    });

    // Print it after deploy
    new CfnOutput(this, "FunctionUrl", { value: funcUrl.url });
  }
}