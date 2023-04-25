import { APP_INITIALIZER, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { HttpClientModule } from '@angular/common/http';
import { BASE_PATH } from './api';
import { EnergyTableComponent } from './energy-table/energy-table.component';
import { DayModalComponent } from './day-modal/day-modal.component';

@NgModule({
  declarations: [AppComponent, EnergyTableComponent, DayModalComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgbModule,
    HttpClientModule,
    FormsModule,
  ],
  // providers: [
  //   {
  //     provide: BASE_PATH,
  //     useValue:
  //   },
  // ],
  bootstrap: [AppComponent],
})
export class AppModule { }
