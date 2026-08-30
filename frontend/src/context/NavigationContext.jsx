import React, { createContext, useContext, useState } from 'react';

const NavigationContext = createContext();

export function NavigationProvider({ children }) {
  // Screens: 'dashboard' | 'detection' | 'gis' | 'attribution' | 'vessel' | 'dossier' | 'alerts' | 'reports' | 'settings' | 'login'
  const [activeScreen, setActiveScreen] = useState('dashboard');
  const [activeIncidentId, setActiveIncidentId] = useState('INC-2026-001');
  const [selectedVesselName, setSelectedVesselName] = useState('MSC Ocean Star');
  const [searchQuery, setSearchQuery] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [unreadAlertsCount, setUnreadAlertsCount] = useState(2);

  const navigateTo = (screen, params = {}) => {
    if (params.incidentId) setActiveIncidentId(params.incidentId);
    if (params.vesselName) setSelectedVesselName(params.vesselName);
    setActiveScreen(screen);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <NavigationContext.Provider
      value={{
        activeScreen,
        setActiveScreen,
        activeIncidentId,
        setActiveIncidentId,
        selectedVesselName,
        setSelectedVesselName,
        searchQuery,
        setSearchQuery,
        isAuthenticated,
        setIsAuthenticated,
        unreadAlertsCount,
        setUnreadAlertsCount,
        navigateTo
      }}
    >
      {children}
    </NavigationContext.Provider>
  );
}

export function useNavigation() {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
}
