import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { TestButtonComponent } from './test-button/test-button.component';
import { HttpClientModule } from '@angular/common/http';
import { BASE_PATH } from './api';

@NgModule({
  declarations: [
    AppComponent,
    TestButtonComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgbModule,
    HttpClientModule
  ],
  providers: [
    {
      provide: BASE_PATH,
      useValue: 'http://localhost:12321'
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
