import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnergyTableComponent } from './energy-table.component';

describe('EnergyTableComponent', () => {
  let component: EnergyTableComponent;
  let fixture: ComponentFixture<EnergyTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EnergyTableComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EnergyTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
