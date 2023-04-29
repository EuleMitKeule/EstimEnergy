import { APP_INITIALIZER, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { HttpClientModule } from '@angular/common/http';
import { BASE_PATH } from './api';
import { EnergyTableComponent } from './energy-table/energy-table.component';
import { DayModalComponent } from './day-modal/day-modal.component';
import { NgxBootstrapIconsModule, allIcons } from 'ngx-bootstrap-icons';
import { NavbarComponent } from './navbar/navbar.component';
import { DeviceTableComponent } from './device-table/device-table.component';
import { EnergyPageComponent } from './energy-page/energy-page.component';
import { DevicesPageComponent } from './devices-page/devices-page.component';
import { DeviceModalComponent } from './device-modal/device-modal.component';
import { environment } from 'src/environments/environment';

@NgModule({
  declarations: [AppComponent, EnergyTableComponent, DayModalComponent, NavbarComponent, DeviceTableComponent, EnergyPageComponent, DevicesPageComponent, DeviceModalComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgbModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    NgxBootstrapIconsModule.pick(allIcons)
  ],
  providers: [
    {
      provide: BASE_PATH,
      useValue: environment.apiUrl,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule { }
