import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnergyPageComponent } from './energy-page.component';

describe('EnergyPageComponent', () => {
  let component: EnergyPageComponent;
  let fixture: ComponentFixture<EnergyPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EnergyPageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EnergyPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
