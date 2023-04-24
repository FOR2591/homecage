import { Module } from '@nestjs/common';
import { ServeStaticModule } from '@nestjs/serve-static';
import { AppController } from './app.controller';
import { AppGateway } from './app.gateway';
import { AppService } from './app.service';

import { join } from 'path';

console.log(join(__dirname, '../..', 'webapp'))
@Module({
  imports: [
    ServeStaticModule.forRoot({
      rootPath: join(__dirname, '../..', 'webapp'),
    })
  ],
  controllers: [AppController],
  providers: [AppGateway, AppService],
})
export class AppModule {}
