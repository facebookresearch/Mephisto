/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


import { useEffect } from 'react';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import urls from 'urls';
import './HomePage.css';


function HomePage() {
  const navigate = useNavigate();
  const { localStorage } = window;

  useEffect(() => {
    localStorage.clear();
    navigate(urls.client.tasks);
  }, [navigate, localStorage]);

  return null;
}


export default HomePage;
