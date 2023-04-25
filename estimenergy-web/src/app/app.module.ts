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
import { NgxBootstrapIconsModule, allIcons } from 'ngx-bootstrap-icons';
import { NavbarComponent } from './navbar/navbar.component';

@NgModule({
  declarations: [AppComponent, EnergyTableComponent, DayModalComponent, NavbarComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgbModule,
    HttpClientModule,
    FormsModule,
    NgxBootstrapIconsModule.pick(allIcons)
  ],
  providers: [
    {
      provide: BASE_PATH,
      useValue: 'http://localhost:12321',
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule { }
