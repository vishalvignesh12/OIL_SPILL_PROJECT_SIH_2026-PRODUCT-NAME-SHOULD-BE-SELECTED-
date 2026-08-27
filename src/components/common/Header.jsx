import React from 'react';
import { useNavigation } from '../../context/NavigationContext';

/**
 * Header Component
 * Top bar with incident context, search, notifications, and officer profile
 */
export default function Header() {
  const { 
    activeIncidentId, 
    activeScreen, 
    navigateTo, 
    unreadAlertsCount,
    searchQuery,
    setSearchQuery 
  } = useNavigation();

  return (
    <header className="h-16 bg-surface-container-lowest border-b border-outline-variant flex justify-between items-center px-6 z-30 shrink-0 sticky top-0">
      {/* Left: Current Active Incident Context */}
      <div className="flex items-center gap-4 shrink-0 min-w-0">
        <h2 className="text-title-lg text-primary font-bold tracking-tight whitespace-nowrap shrink-0">
          Maritime Intel
        </h2>

        {/* Incident Badge Group */}
        <div className="hidden sm:flex items-center gap-2.5 pl-4 border-l border-outline-variant shrink-0 whitespace-nowrap">
          <span 
            onClick={() => navigateTo('dossier', { incidentId: activeIncidentId })}
            className="cursor-pointer text-[11px] leading-none bg-error-container text-on-error-container px-2.5 py-1.5 rounded font-bold uppercase tracking-wider hover:opacity-90 transition-opacity whitespace-nowrap shrink-0 inline-flex items-center"
            title="Jump to Incident Dossier"
          >
            {activeIncidentId}
          </span>
          <span className="text-[13px] text-on-surface-variant flex items-center gap-1 whitespace-nowrap shrink-0 font-medium">
            <span className="material-symbols-outlined text-[16px] text-secondary">location_on</span>
            Bay of Bengal
          </span>
          <span className="text-[12px] leading-none bg-secondary-container text-on-secondary-container px-2.5 py-1.5 rounded border border-secondary/20 flex items-center gap-1.5 font-semibold whitespace-nowrap shrink-0 inline-flex">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse shrink-0"></span>
            94% Confidence
          </span>
        </div>
      </div>

      {/* Right: Search, Security Alert Badge, and Officer Avatar */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Quick Search */}
        <div className="relative hidden lg:block w-48 xl:w-64 shrink-0">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">
            search
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search vessels, coords..."
            className="w-full pl-9 pr-4 py-1.5 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-outline"
          />
        </div>

        {/* Alerts Button */}
        <button
          onClick={() => navigateTo('alerts')}
          className="relative w-9 h-9 rounded flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors shrink-0"
          title="Security Alerts"
        >
          <span className="material-symbols-outlined text-[20px]">notifications</span>
          {unreadAlertsCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-error rounded-full ring-2 ring-surface-container-lowest animate-pulse"></span>
          )}
        </button>

        {/* GIS Forensics Quick Jump */}
        <button
          onClick={() => navigateTo('gis')}
          className={`w-9 h-9 rounded flex items-center justify-center transition-colors shrink-0 ${
            activeScreen === 'gis' ? 'bg-primary-container text-on-primary' : 'text-on-surface-variant hover:bg-surface-container-high'
          }`}
          title="GIS Map Workspace"
        >
          <span className="material-symbols-outlined text-[20px]">map</span>
        </button>

        {/* User / Officer Profile */}
        <div 
          onClick={() => navigateTo('settings')}
          className="flex items-center gap-2.5 pl-3 border-l border-outline-variant cursor-pointer hover:opacity-80 transition-opacity shrink-0"
          title="Officer Settings"
        >
          <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold text-label-sm shrink-0">
            RV
          </div>
          <div className="hidden xl:block text-left whitespace-nowrap">
            <div className="text-label-sm font-bold text-primary leading-tight">Cmdr. R. Verma</div>
            <div className="text-[11px] text-on-surface-variant leading-tight">Surveillance Command</div>
          </div>
        </div>
      </div>
    </header>
  );
}
